from fastapi import APIRouter, Header, Form, Depends
from starlette.responses import RedirectResponse

from app.deps import get_session_id
from app.fasthtml import render, url_for

router = APIRouter()


# Routes
@router.get("/")
async def home_page(session_id: str = Depends(get_session_id)):
    """Render the home page."""

    active_games = []

    # If a player exists for this session
    if player := Player.get(session_id=session_id):
        pass
        # Get active games
        # active_games = Game.filter(players)

    return await render("index.html", {"active_games": active_games})


@router.get("/create-player")
async def player_form(block_name: str = Header(None)):
    """Render the player creation form."""

    return await render(f"player_form_dialog.html#{block_name}")


@router.post("/create-player")
async def submit_player_form(
    session_id: str = Depends(get_session_id),
    name: str = Form(...),
    avatar: int = Form(1),
):
    """Creates player and redirects to homepage."""

    Player.get_or_create(
        session_id=session_id,
        name=name,
        avatar=avatar,
    )

    return RedirectResponse(
        url=url_for("home_page"),
        status_code=302,
    )


@router.post("/create")
async def create_game(player: Player = Depends(get_player_from_session)):
    """Create game, add player as host, and redirect to game page."""

    game = await Game.create()

    await game.add_player(player)

    await game.set_host(player)

    await game.save()

    return RedirectResponse(
        url=url_for("game_page", game_code=game.code),
        status_code=302,
    )


@router.post("/join")
async def join_game(
    game: Game = Depends(get_current_game),
    player: Player = Depends(get_current_player),
):
    """Joins player to game and redirects to game page."""

    # Validate game is accepting players
    if not game.is_in_lobby:
        raise HTTPException(
            status_code=403, detail="Game already started or is finished"
        )

    # Check if player is already in this game
    existing_connection = find_player_connection_by_session_key(
        game, player.session_key
    )
    if existing_connection:
        # Player already in game, just redirect
        return RedirectResponse(f"/{game.code}", status_code=302)

    # Create new connection and redirect
    await create_player_connection(db, player=player, game=game)
    return RedirectResponse(f"/{game.code}", status_code=302)


@router.get("/{game_code}", response_class=HTMLResponse)
async def get_game(
    request: Request,
    player_connection: PlayerConnection = Depends(get_current_player_connection),
):
    """Game detail page with current state."""

    return templates.TemplateResponse(
        "game.html",
        {
            "request": request,
            "game": player_connection.game,
            "current_player": player_connection.player,
        },
    )


# @app.post("/{game_code}/start")
# async def start_game(
#     game_code: str,
#     db: AsyncSession = Depends(get_database_session),
# ):
#     """Start a new game round."""
#     # Get game and current player
#     # game = await get_game_by_code(db, code=game_code)
#     # if not game:
#     #     return HTMLResponse(content="No game found with that code.", status_code=404)
#
#     # current_player = await get_player_by_session(db, game=game, session_key=session_key)
#     # if not current_player:
#     #     return HTMLResponse(content="Player not found.", status_code=404)
#     #
#     # # Check if current player is the host
#     # if current_player != game.host:
#     #     return HTMLResponse(
#     #         content="Only the host can start the game.", status_code=404
#     #     )
#
#     # await start_new_turn(game.code)
#
#     # Start background task if not already running
#     # if game.code not in _running_games:
#     #     task = asyncio.create_task(run_game_in_background(game.code))
#     #     _running_games[game.code] = task
#
#     # Clean up when task finishes
#     # def cleanup(task):
#     #     if game.code in _running_games:
#     #         del _running_games[game.code]
#
#     # task.add_done_callback(cleanup)
#
#     await start_game_in_background(game_code, db=db)
#
#     return {"status": "OK"}
#
#
#
#
# @app.get("/{game_code}/events")
# async def get_game_events(
#     request: Request,
#     connection: PlayerConnection = Depends(get_current_player_connection),
#     db: AsyncSession = Depends(get_database_session),
#     nats_connection: NATS = Depends(get_nats_connection),
# ):
#     """HTMX SSE endpoint: Sends entire page HTML on NATS 'refresh' events."""
#     queue = asyncio.Queue()
#
#     # Store values before entering async context to avoid detached instance errors
#     game_code = connection.game.code
#     player_session_key = connection.player.session_key
#
#     async def event_generator():
#         async def nats_callback(msg):
#             await queue.put("game_changed")
#
#         await nats_connection.subscribe(f"game.{game_code}", cb=nats_callback)
#
#         while True:
#             await queue.get()  # Wait for game change event
#
#             db.expire_all()  # Ensure we get fresh data
#
#             # Get fresh game and player data
#             fresh_game = await get_game_by_code(db, code=game_code)
#             fresh_player = next(
#                 (
#                     conn.player
#                     for conn in fresh_game.connections
#                     if conn.player.session_key == player_session_key
#                 ),
#                 None,
#             )
#
#             response = templates.TemplateResponse(
#                 "game.html",
#                 {
#                     "request": request,
#                     "game": fresh_game,
#                     "current_player": fresh_player,
#                 },
#                 block_name="game_state",
#             )
#             html = response.body.decode()
#             yield {"event": "refreshGame", "data": html}
#
#     return EventSourceResponse(event_generator())
#
#
# @app.post("/{game_code}/heartbeat")
# async def heartbeat(
#     connection: PlayerConnection = Depends(get_current_player_connection),
#     db: AsyncSession = Depends(get_database_session),
# ):
#     """Update connection's last heartbeat timestamp and check for inactive connections."""
#
#     await update_player_connection_heartbeat(db, connection=connection)
#
#     await mark_stale_connections_as_inactive(db, game=connection.game)
#
#     return Response(status_code=204)
