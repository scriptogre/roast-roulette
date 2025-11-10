from datetime import datetime

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from main.enums import GameStatus
from main.models import Game, Player, PlayerConnection


# --- CREATE ---


async def create_game(db: AsyncSession) -> Game:
    game = Game()
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def update_game_host(db: AsyncSession, *, game: Game, player: Player) -> None:
    """Set a player as the host of a game."""
    game.host_id = player.id
    db.add(game)
    await db.commit()


async def get_or_create_player(
    db: AsyncSession,
    *,
    session_key: str,
    name: str,
    avatar: int = 1,
) -> Player:
    """Get existing player or create new one."""
    # Check if player already exists
    result = await db.execute(select(Player).where(Player.session_key == session_key))
    player = result.scalars().first()

    if player:
        return player

    # Create new player
    player = Player(
        name=name,
        avatar=avatar,
        session_key=session_key,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


async def create_player_connection(
    db: AsyncSession,
    *,
    player: Player,
    game: Game,
) -> PlayerConnection:
    """Create a connection between player and game."""
    connection = PlayerConnection(
        player_id=player.id,
        game_id=game.id,
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


# --- READ ---


async def get_game_by_code(db: AsyncSession, *, code: str) -> Game | None:
    # Eager load connections and their players, plus host
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.connections).selectinload(PlayerConnection.player),
            selectinload(Game.host),
        )
        .where(Game.code == code.upper())
    )
    return result.scalars().first()


async def get_player_by_session_key(
    db: AsyncSession, *, session_key: str
) -> Player | None:
    """Get a player by session key."""
    result = await db.execute(select(Player).where(Player.session_key == session_key))
    return result.scalars().first()


async def get_user_active_games(db: AsyncSession, *, session_key: str) -> list[Game]:
    """Get all active games where the user is a player."""
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.connections).selectinload(PlayerConnection.player),
            selectinload(Game.host),
        )
        .join(PlayerConnection)
        .join(Player)
        .where(Player.session_key == session_key)
        .where(Game.status != GameStatus.FINISHED)
        .order_by(Game.updated_at.desc())
    )
    return list(result.scalars().all())


# --- UPDATE ---


async def update_player_connection_heartbeat(
    db: AsyncSession, *, connection: PlayerConnection
) -> bool:
    """Update connection's heartbeat and reactivate if needed. Returns True if connection status changed."""
    was_active = connection.is_active
    connection.last_heartbeat = datetime.now()

    # Only commit if connection status changed (reactivation)
    if not was_active:
        connection.is_active = True
        connection.updated_at = datetime.now()
        connection.activity_changed_at = datetime.now()
        await db.commit()
        return True  # Connection status changed
    else:
        await db.commit()
        return False  # No status change


async def mark_stale_connections_as_inactive(db: AsyncSession, *, game: Game) -> None:
    """Find connections with stale heartbeats and mark them as inactive."""
    try:
        # First, let's see what connections exist in this game
        check_result = await db.execute(
            text("""
            SELECT c.id, p.name, c.is_active, c.last_heartbeat, 
                   NOW() - c.last_heartbeat as time_since_heartbeat
            FROM connection c
            JOIN player p ON c.player_id = p.id
            WHERE c.game_id = :game_id
            """),
            {"game_id": game.id},
        )
        connections_info = check_result.fetchall()
        print(
            f"Connections in game {game.code}: {[(c.name, c.is_active, c.time_since_heartbeat) for c in connections_info]}"
        )

        # Now do the actual update
        result = await db.execute(
            text("""
            UPDATE connection 
            SET is_active = false, updated_at = NOW(), activity_changed_at = NOW()
            WHERE game_id = :game_id 
            AND is_active = true
            AND last_heartbeat < NOW() - INTERVAL '5 seconds'
            """),
            {"game_id": game.id},
        )
        print(
            f"Disconnection check for game {game.code}: {result.rowcount} connections marked as inactive"
        )
        if result.rowcount > 0:
            await db.commit()
            print(f"Committed disconnection changes for game {game.code}")
    except Exception as e:
        print(f"ERROR in mark_stale_heartbeat_connections_as_inactive: {e}")
        raise


# --- DELETE ---
