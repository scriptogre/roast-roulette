# """
# FastAPI dependencies for roast-roulette application.
# """
from fastapi import Request, Depends, HTTPException, status
import uuid


# =============================================================================
# SESSION KEY DEPENDENCIES
# =============================================================================


async def get_session_id(request: Request) -> str:
    """
    Ensures a session exists for the current request.
    """

    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4()).replace("-", "")[:32]

    return request.session["session_id"]


async def get_current_player(
    session_id: str = Depends(get_session_id),
) -> Player:
    """
    Gets player associated with the current session.
    """
    player = await Player.get(session_id=session_id)

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    return player


# # =============================================================================
# # NATS DEPENDENCIES
# # =============================================================================
#
# _nats_connection: NATS | None = None
#
#
# async def get_nats_connection(request: Request) -> NATS:
#     """NATS connection dependency."""
#
#     if _nats_connection is None:
#         _nats_connection = await nats.connect(settings.NATS_URL)
#     return _nats_connection
#
#
# # =============================================================================
# # GAME DEPENDENCIES
# # =============================================================================
#
#
# def find_player_connection_by_session_key(
#     game: Game, session_key: str
# ) -> PlayerConnection | None:
#     """Find a player connection in the game by session key."""
#     return next(
#         (conn for conn in game.connections if conn.player.session_key == session_key),
#         None,
#     )
#
#
# async def get_current_game(
#     request: Request,
#     db: AsyncSession = Depends(get_database_session),
# ) -> Game:
#     """
#     Validates game exists and is accessible.
#     Handles game_code from both path parameters and form data to avoid duplicating validation logic.
#     Throws appropriate HTTP exceptions for invalid cases.
#     """
#     # Try path parameter first
#     game_code = request.path_params.get("game_code")
#
#     # If not found, try form data
#     if not game_code:
#         form = await request.form()
#         game_code = form.get("game_code")
#
#     if not game_code:
#         raise HTTPException(status_code=400, detail="game_code required")
#
#     # Validate game exists
#     game = await get_game_by_code(db, code=game_code)
#     if not game:
#         raise HTTPException(status_code=404, detail="Game not found")
#
#     # Check if game is finished
#     if game.is_finished:
#         raise HTTPException(status_code=410, detail="Game has ended")
#
#     return game
#
#
#
#
# async def get_current_player_connection(
#     game: Game = Depends(get_current_game),
#     player: Player = Depends(get_current_player),
# ) -> PlayerConnection:
#     """
#     Gets the current player's connection to the current game.
#     Validates that the player is actually in the game by finding their connection.
#     """
#     connection = find_player_connection_by_session_key(game, player.session_key)
#
#     if not connection:
#         # User is not a player in this game
#         if game.is_in_progress:
#             raise HTTPException(
#                 status_code=403, detail="Game already started and you are not a player"
#             )
#         else:
#             # Redirect to join form with game code
#             redirect_url = f"/join?game_code={game.code}"
#             raise HTTPException(
#                 status_code=307,
#                 detail="Redirect to join",
#                 headers={"HX-Location": redirect_url},
#             )
#
#     return connection
