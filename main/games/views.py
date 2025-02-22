"""
Handles HTTP requests/responses for the 'games' app. Includes logic for creating/joining games,
uploading photos, spinning the "roast roulette," and submitting clapbacks.
"""

import threading

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from .consumers import refresh_game
from .models import Game
from .models import Round
from .services import generate_roast_pieces


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
        return render(request, 'games/game_form.jinja')
    else:
        # Retrieve form data
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')

        # Create new game instance
        game = Game.objects.create()

        # Add the host player to the game
        player = game.add_player(player_name, avatar, request.session.session_key)
        player.is_host = True
        player.save()

        # Redirect to game page
        return redirect('games:detail', game_code=game.code)


@require_http_methods(['GET', 'POST'])
def game_join_view(request):
    """
    Handles game joining.

    - GET: Shows a form to enter player name and game code.
    - POST: Adds a player to an existing game and redirects to the game page.
    """

    if request.method == 'GET':
        # Render join game form
        return render(request, 'games/game_form.jinja', {'is_joining': True})

    else:  # request.method == 'POST':
        # Retrieve form data
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')
        game_code = request.POST.get('game_code').upper()

        try:
            # Get game instance by code
            game = Game.objects.get(code=game_code)
            # Add player to game
            game.add_player(player_name, avatar, session_id=request.session.session_key)
            # Refresh game in all connected clients
            refresh_game(game_code)
            # Redirect to game page
            return redirect('games:detail', game_code=game.code)

        except ValidationError as e:
            # Return an error response with validation message
            return HttpResponse(f'Failed to join game: {e}')

        except Game.DoesNotExist:
            # Return an error response with message
            return HttpResponse('Game not found.')


@require_GET
def game_detail_view(request, game_code):
    """
    Displays the game lobby with details like players, rounds, and uploaded photos.
    """

    # Retrieve game and current player
    game = get_object_or_404(Game, code=game_code)
    current_player = game.players.get(session_id=request.session.session_key)

    template_name = 'games/game_detail.jinja'

    return render(
        request,
        template_name,
        {
            'game': game,
            'round': game.current_round,
            'player': current_player,
        },
    )


@require_POST
def game_start_view(request, game_code):
    """
    Handles starting the game.
    """

    # Retrieve game and current player
    game = get_object_or_404(Game, code=game_code)
    players = game.players.all()

    # Check if player is host
    current_player = players.get(session_id=request.session.session_key)
    if not current_player.is_host:
        return HttpResponse('Only the host can start the game!', status=403)

    # Start game
    round = game.start_round()

    # "Photo Submission" Phase
    # ----------------------
    round.state = Round.State.SUBMIT_PHOTOS
    round.save()
    refresh_game(game_code)
    round.wait_for_players()

    # Pick a random target photo
    target_photo = round.pick_target_photo()

    # Create a container for thread results
    thread_results = {'roast_pieces': None}

    # Define the function to run in background
    def generate_roasts_background():
        thread_results['roast_pieces'] = generate_roast_pieces(
            target_photo, count=players.count() * 5
        )

    # Start the background thread for roast generation
    roast_thread = threading.Thread(target=generate_roasts_background)
    roast_thread.start()

    # Meanwhile, proceed to "Show Target" Phase
    round.state = Round.State.SHOW_TARGET
    round.save()
    refresh_game(game_code)
    round.wait_for_players()

    # Wait for roast generation to complete if it hasn't already
    roast_thread.join()

    # Generate roast pieces for each player
    roast_pieces = thread_results['roast_pieces']
    for player in players:
        player.add_roast_pieces([text for text in roast_pieces[:5]])
        roast_pieces = roast_pieces[5:]

    # "Submit Pieces" Phase
    # ------------------------
    round.state = Round.State.SUBMIT_ROASTS
    round.save()
    refresh_game(game_code)
    round.wait_for_players()

    # Return a success response
    return HttpResponse(status=204)


@require_POST
def upload_photo_view(request, game_code):
    """
    Handles photo uploads from players.
    """

    # Retrieve game and current player
    game = get_object_or_404(Game, code=game_code.upper())
    player = game.players.get(session_id=request.session.session_key)
    uploaded_photo_file = request.FILES.get('photo')

    if player and uploaded_photo_file:
        try:
            # Add photo
            player.add_photo(uploaded_photo_file)

            # Refresh game in all connected clients
            refresh_game(game_code)

            return HttpResponse(status=204)

        except ValidationError as e:
            # Return an error response with validation message
            return HttpResponse(f'Failed to upload photo: {e}', status=400)

    # Return a generic error response
    return HttpResponse('Failed to upload photo.', status=400)
