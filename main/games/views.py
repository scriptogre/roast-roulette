"""
Handles HTTP requests/responses for the 'games' app. Includes logic for creating/joining games,
uploading photos, spinning the "roast roulette," and submitting clapbacks.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from .models import Game
from .models import Player


def index_view(request):
    # Create user session if it doesn't exist
    if not request.session.session_key:
        request.session.create()

    """Renders the homepage where users can create or join a game."""
    return render(request, 'index.jinja')


@require_http_methods(['GET', 'POST'])
def game_create_view(request):
    """
    Handles game creation.

    - GET: Shows a form to enter player name and select an avatar.
    - POST: Creates a new game, adds the host player, and redirects to the game page.
    """
    # Create user session if it doesn't exist
    if not request.session.session_key:
        request.session.create()

    if request.method == 'GET':
        # Show form for selecting player name and avatar
        return render(request, 'games/game_form.jinja')

    else:  # request.method == 'POST':
        # Get player name & avatar from form
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')

        # Create game
        game = Game.objects.create()

        # Add this player to game
        player = game.add_player(
            player_name, avatar, session_id=request.session.session_key
        )
        player.is_host = True
        player.save()

        return redirect('games:detail', game_code=game.code)


@require_http_methods(['GET', 'POST'])
def game_join_view(request):
    """
    Handles game joining.

    - GET: Shows a form to enter player name and game code.
    - POST: Adds a player to an existing game and redirects to the game page.
    """
    # Create user session if it doesn't exist
    if not request.session.session_key:
        request.session.create()

    if request.method == 'GET':
        return render(request, 'games/game_form.jinja', {'is_joining': True})

    else:  # request.method == 'POST':
        # Get player name & game code from form (note: <input> should have an attribute 'name="player_name"')
        player_name = request.POST.get('player_name')
        avatar = request.POST.get('avatar')
        game_code = request.POST.get('game_code').upper()

        # Get games by code
        game = get_object_or_404(Game, code=game_code)

        # Add player to game
        game.add_player(player_name, avatar, session_id=request.session.session_key)

        # Send data to all clients listening in the group "game_{game_code}"
        async_to_sync(get_channel_layer().group_send)(
            game_code, {'type': 'update_game'}
        )

        return redirect('games:detail', game_code=game.code)


@require_GET
def game_detail_view(request, game_code):
    """Displays the game lobby with details like players, rounds, and uploaded photos."""
    # TODO: Ensure that only players in the game can access this view

    # Create user session if it doesn't exist
    if not request.session.session_key:
        request.session.create()

    game = get_object_or_404(Game, code=game_code)

    # Get player by session ID (if exists)
    player = Player.objects.get(session_id=request.session.session_key, game=game)

    return render(request, 'games/game_detail.jinja', {'game': game, 'player': player})


@require_POST
def upload_photo_view(request, game_code):
    """Handles photo uploads from players."""
    # TODO: Ensure that only players in the game can upload photos
    # TODO 2: Track for which round the photo was uploaded

    # Ensure game code is always uppercase
    game_code = game_code.upper()

    game = get_object_or_404(Game, code=game_code)
    player = None
    uploaded_photo = request.FILES.get('photo')

    if request.session.session_key:
        player = Player.objects.get(session_id=request.session.session_key, game=game)

    if player and uploaded_photo:
        game.add_photo(player, uploaded_photo)
        return HttpResponse('Your photo has been uploaded successfully! 🎉')

    return HttpResponse('Failed to upload photo. Please try again.')


def spin_roulette_view(request):
    pass

    # TODO: Implement this view
    # 1. Get the game for which the roulette is being spun (using the game_code parameter from the URL)
    # 2. Get all photos uploaded for that round and select one at random
    # 3. Use OpenAI API to create an AI roast for that selected photo
    # 4. Render the resulted roast and the selected photo


def submit_clapback_view(request, roast_id):
    pass

    # TODO: Implement this view
    # 1. Get the roast for which the clapback is being submitted (using the roast_id parameter from the URL)
    # 2. Get the clapback text from the form data (from the user's POST request)
    # 3. Save the clapback text to the roast object
    # 4. Render the clapback text on the page
