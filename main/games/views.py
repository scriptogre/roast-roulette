from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from main.games.enums import GameRoundStage
from main.games.services.crud import (
    create_game,
    create_host_player,
    create_player,
    create_photo,
    create_vote,
    delete_vote,
    get_game_by_code,
    get_player_by_session,
    get_players,
    get_current_game_round,
    get_photos,
    get_roasts,
    get_target_photo,
    get_photo_uploaded_by_player,
    get_roast_by_id,
    get_vote_by_id,
    create_game_round,
)
from main.games.services.game_flow import play_game_round_in_background


@require_GET
async def index_view(request):
    """
    Renders the homepage where users can create or join a game.
    """
    return render(request, 'index.jinja')


@require_http_methods(['GET', 'POST'])
async def game_create_view(request):
    """
    Handles logic for creating games.

    - GET: Shows form to choose avatar and player name.
    - POST: Creates game & host player, and redirects to game.
    """
    match request.method:
        case 'GET':
            return render(request, 'games/game_form.jinja', {'is_joining': False})

        case 'POST':
            game = await create_game()

            await create_host_player(
                game=game,
                player_name=request.POST.get('player_name'),
                avatar=request.POST.get('avatar'),
                session_key=request.session.session_key
            )

            return redirect('games:detail', game_code=game.code)


@require_http_methods(['GET', 'POST'])
async def game_join_view(request):
    """
    Handles logic for joining games.

    - GET: Shows form to choose avatar, player name, and game code.
    - POST: Creates player and redirects to game.
    """
    match request.method:
        case 'GET':
            return render(
                request,
                'games/game_form.jinja',
                {
                    'is_joining': True,
                    'game_code': request.GET.get('game_code', '').upper()
                }
            )

        case 'POST':
            game = await get_game_by_code(code=request.POST.get('game_code').upper())
            if not game:
                return HttpResponse('Game not found.', status=404)
            if not game.is_in_lobby:
                return HttpResponse('Game has already started or is finished.', status=403)

            await create_player(
                game=game,
                player_name=request.POST.get('player_name'),
                avatar=request.POST.get('avatar'),
                session_key=request.session.session_key
            )

            return redirect('games:detail', game_code=game.code)


@require_GET
async def game_detail_view(request, game_code: str):
    game = await get_game_by_code(code=game_code)
    players = await get_players(game=game)
    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)

    if current_player not in players:
        return redirect('games:join')

    context = {
        'game': game,
        'players': players,
        'current_player': current_player,
    }
    if game.is_in_progress:
        game_round = await get_current_game_round(game=game)

        context.update(
            {
                'game_round': game_round,
                'photos': await get_photos(game_round=game_round),
                'roasts': await get_roasts(game_round=game_round),
                'target_photo': await get_target_photo(game_round=game_round),
                'current_player_photo': await get_photo_uploaded_by_player(game_round=game_round, player=current_player),
            }
        )

    return render(request, 'games/game_detail.jinja', context)


@require_POST
async def game_round_start_view(request, game_code: str):
    game = await get_game_by_code(code=game_code)

    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)
    if not current_player.is_host:
        return HttpResponse('Only the host can start the game round.', status=403)

    game_round = await create_game_round(game=game)

    # Assign variable to prevent garbage collector from deleting background task
    _ = await play_game_round_in_background(game=game, game_round=game_round)

    return HttpResponse(status=204, headers={'HX-Trigger': 'refreshGame'})


@require_POST
async def photo_upload_view(request, game_code):
    game = await get_game_by_code(code=game_code)
    game_round = await get_current_game_round(game=game)

    if game.is_in_lobby:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.stage != GameRoundStage.UPLOAD_PHOTO:
        return HttpResponse('Not the photo upload phase.', status=403)

    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)

    await create_photo(game_round=game_round, player=current_player, uploaded_file=request.FILES.get('photo'))

    return HttpResponse(status=204, headers={'HX-Trigger': 'refreshGame'})


@require_POST
async def photo_caption_submit_view(request, game_code):
    game = await get_game_by_code(code=game_code)
    game_round = await get_current_game_round(game=game)

    if not game.is_in_progress:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.stage != GameRoundStage.UPLOAD_PHOTO:
        return HttpResponse('Not the photo upload phase.', status=403)

    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)

    current_player_photo = await get_photo_uploaded_by_player(game_round=game_round, player=current_player)
    current_player_photo.caption = request.POST.get('caption')
    await current_player_photo.asave()

    return HttpResponse(status=204)


@require_POST
async def vote_create_view(request, game_code, roast_id):
    game = await get_game_by_code(code=game_code)
    game_round = await get_current_game_round(game=game)

    if not game.is_in_progress:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.stage != GameRoundStage.VOTE_ROASTS:
        return HttpResponse('Not the roast voting phase.', status=403)

    roast = await get_roast_by_id(game_round=game_round, roast_id=roast_id)
    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)

    if roast.is_already_voted_by(current_player):
        return HttpResponse('Roast voted already.')

    await create_vote(roast=roast, submitted_by=current_player)

    return HttpResponse(status=204)


@require_POST
async def vote_delete_view(request, game_code: str, roast_id, vote_id):
    game = await get_game_by_code(code=game_code)
    game_round = await get_current_game_round(game=game)

    if not game.is_in_progress:
        return HttpResponse('Game is not in progress.', status=403)
    if game_round.stage != GameRoundStage.VOTE_ROASTS:
        return HttpResponse('Not the roast voting phase.', status=403)

    roast = await get_roast_by_id(game_round=game_round, roast_id=roast_id)
    current_player = await get_player_by_session(game=game, session_key=request.session.session_key)

    vote = await get_vote_by_id(roast=roast, submitted_by=current_player, vote_id=vote_id)
    if not vote:
        return HttpResponse('There\'s no vote to delete.')

    await delete_vote(vote=vote)

    return HttpResponse(status=204)
