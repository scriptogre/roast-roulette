from contextlib import asynccontextmanager

import nats
import asyncpg
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    pg_connection: asyncpg.Connection = await asyncpg.connect(settings.DATABASE_URL)
    nats_connection: nats.NATS = await nats.connect(settings.NATS_URL)

    # Store in app state
    app.state.pg_connection = pg_connection
    app.state.nats_connection = nats_connection

    # Forward notifications from Postgres -> NATS
    async def on_game_change(conn, pid, channel, game_code):
        await nats_connection.publish(f"game.{game_code}")

    await pg_connection.add_listener("game_change", on_game_change)

    # Register ORM
    async with RegisterTortoise(
        app, config=settings.TORTOISE_ORM, generate_schemas=True
    ):
        yield

    # Clean up
    await pg_connection.remove_listener("game_updated", on_game_change)
    await pg_connection.close()
    await nats_connection.close()
