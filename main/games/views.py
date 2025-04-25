from uuid import uuid4

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from .consumers import trigger_clients_refresh
from .enums import GameRoundState, GameState
from .models import Game, RoastIdeaVote
from .services import (
    generate_roast_poem,
    generate_roast_ideas_in_the_background,
    generate_roast_poem_in_the_background,
)


@require_GET
def index_view(request):
    """
    Renders the homepage where users can create or join a game.
    """

    return render(request, 'index.jinja')


@require_http_methods(['GET', 'POST'])
def game_create_view(request):
    """
    Handles game creation.
    - GET: Shows a form to enter player name and select an avatar.
    - POST: Creates a new game, adds the host player, and redirects to the game page.
    """

    if request.method == 'GET':
        # Render create game form
        return render(request, 'games/game_form.jinja', {'is_joining': False})
    else:
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')

        game = Game.objects.create()

        player = game.add_player(player_name, avatar, request.session.session_key)
        player.is_host = True
        player.save()

        return redirect('games:detail', game_code=game.code)


@require_http_methods(['GET', 'POST'])
def game_join_view(request):
    """
    Handles game joining.

    - GET: Shows a form to enter player name and game code.
    - POST: Adds a player to an existing game and redirects to the game page.
         Only allows joining if the game is WAITING_FOR_PLAYERS.
    """

    if request.method == 'GET':
        game_code = request.GET.get('game_code', '').upper()
        return render(
            request,
            'games/game_form.jinja',
            {'is_joining': True, 'game_code': game_code},
        )

    else:  # request.method == 'POST':
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')
        game_code = request.POST.get('game_code').upper()

        game = Game.objects.filter(code=game_code).first()
        if not game:
            return HttpResponse('Game not found.', status=404)
        if game.state != GameState.WAITING_FOR_PLAYERS:
            return HttpResponse('Game has already started or is finished.', status=403)

        game.add_player(player_name, avatar, session_id=request.session.session_key)

        trigger_clients_refresh(game_code)

        return redirect('games:detail', game_code=game.code)


@require_GET
def game_detail_view(request, game_code):
    """
    Displays the game lobby or the game's current round screen.
    """
    game = get_object_or_404(Game, code=game_code)

    if not game.players.filter(session_id=request.session.session_key).exists():
        return redirect(reverse('games:join') + f'?game_code={game_code}')

    current_player = game.players.get(session_id=request.session.session_key)

    return render(
        request,
        'games/game_detail.jinja',
        {
            'game': game,
            'player': current_player,
        },
    )


@require_POST
def game_round_start_view(request, game_code):
    """
    Starts the next round of the game.
    Only allowed if the game is WAITING_FOR_PLAYERS or IN_PROGRESS.
    Sets the game state to IN_PROGRESS.
    """
    game = get_object_or_404(Game, code=game_code)

    # Verify game state
    if game.state not in [GameState.WAITING_FOR_PLAYERS, GameState.IN_PROGRESS]:
        return HttpResponse('Game is finished or aborted.', status=403)

    # Verify player is host
    current_player = game.players.get(session_id=request.session.session_key)
    if not current_player.is_host:
        return HttpResponse('Only hosts can start the round', status=403)

    # Update game state if necessary
    if game.state == GameState.WAITING_FOR_PLAYERS:
        game.state = GameState.IN_PROGRESS
        game.save()

    # Start the next round
    game_round = game.start_next_round()

    # --- UPLOAD PHOTO ---
    game_round.state = GameRoundState.UPLOAD_PHOTO
    game_round.save()
    trigger_clients_refresh(game_code)
    game_round.wait_for_players()

    # Abort if no photos uploaded
    if not game_round.photos.exists():
        game.rounds.filter(id=game_round.id).delete()
        trigger_clients_refresh(game_code)
        return HttpResponse('No photos uploaded, cannot continue round.', status=400)

    roast_target_photo = game_round.choose_roast_target()

    future = generate_roast_ideas_in_the_background(
        roast_target_photo, count=20,
    )

    # --- CHOOSE ROAST TARGET (ROULETTE) ---
    game_round.state = GameRoundState.CHOOSE_ROAST_TARGET
    game_round.save()
    trigger_clients_refresh(game_code)
    game_round.wait_for_players()

    generated_roast_ideas = future.result()
    for text in generated_roast_ideas:
        game_round.add_roast_idea(text)

    # --- VOTE ROAST IDEAS ---
    game_round.state = GameRoundState.VOTE_ROAST_IDEAS
    game_round.save()
    trigger_clients_refresh(game_code)
    game_round.wait_for_players()

    future = generate_roast_poem_in_the_background(
        roast_target_photo,
        roast_ideas=[idea.text for idea in game_round.roast_ideas.all()],
    )

    # -- SHOW MOST VOTED IDEAS --
    game_round.state = GameRoundState.SHOW_MOST_VOTED_IDEAS
    game_round.save()
    trigger_clients_refresh(game_code)
    game_round.wait_for_players()

    # Create the roast ideas
    generated_poem_text = future.result()
    game_round.add_roast_poem(generated_poem_text)

    # --- SHOW ROAST POEM ---
    game_round.state = GameRoundState.SHOW_ROAST_POEM
    game_round.save()
    trigger_clients_refresh(game_code)

    return HttpResponse(status=204)


@require_POST
def photo_upload_view(request, game_code):
    """
    Handle photo uploads from players during GameRoundState.UPLOAD_PHOTO stage.
    Only allowed if the game is IN_PROGRESS.
    """
    game = get_object_or_404(Game, code=game_code.upper())
    game_round = game.round

    if game.state != GameState.IN_PROGRESS:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.state != GameRoundState.UPLOAD_PHOTO:
        return HttpResponse('Not the photo upload phase.', status=403)

    player = game.players.get(session_id=request.session.session_key)
    uploaded_photo_file = request.FILES.get('photo')

    cache_key = f'photo:{uuid4()}'
    cache.set(cache_key, uploaded_photo_file.read(), timeout=3600)

    # Create photo record
    game_round.add_photo_for(player, cache_key)

    return HttpResponse(status=204, headers={'HX-Trigger': 'refreshGame'})


@require_POST
def photo_caption_submit_view(request, game_code):
    game = get_object_or_404(Game, code=game_code.upper())
    game_round = game.round

    if game.state != GameState.IN_PROGRESS:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.state != GameRoundState.UPLOAD_PHOTO:
        return HttpResponse('Not the photo upload phase.', status=403)

    player = game.players.get(session_id=request.session.session_key)
    photo = game_round.photo_for(player)
    photo.caption = request.POST.get('caption')
    photo.save()

    return HttpResponse(status=204)


@require_POST
def roast_idea_toggle_vote_view(request, game_code, roast_idea_id):
    game = get_object_or_404(Game, code=game_code.upper())
    game_round = game.round

    if game.state != GameState.IN_PROGRESS:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.state != GameRoundState.VOTE_ROAST_IDEAS:
        return HttpResponse('Not the roast ideas voting phase.', status=403)

    roast_idea = game_round.roast_ideas.get(id=roast_idea_id)
    player = game.players.get(session_id=request.session.session_key)

    existing_vote = RoastIdeaVote.objects.filter(
        player=player, roast_idea=roast_idea
    ).first()

    if existing_vote:
        existing_vote.delete()
    else:
        game_round.add_roast_idea_vote(player, roast_idea)

    return HttpResponse(status=204)
