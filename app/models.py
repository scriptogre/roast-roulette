from typing import Self

import string
import random

from enum import Enum

from tortoise import Model
from tortoise.fields import (
    IntField,
    DatetimeField,
    CharField,
    ReverseRelation,
    CharEnumField,
    ForeignKeyField,
    SET_NULL,
    BooleanField,
    CASCADE,
)

from app.tortoise_lifecycle import LifecycleMixin, after_create, after_update


def generate_unique_game_code():
    """Generates a short, unique 4-character code using uppercase letters."""
    return "".join(random.choices(string.ascii_uppercase, k=4))


class BaseModel(LifecycleMixin, Model):
    """Base model with timestamps."""

    id = IntField(primary_key=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class Player(BaseModel):
    """
    Represents a player with a unique session.
    """

    session_id = CharField(max_length=32, unique=True)
    name = CharField(max_length=32)
    avatar = IntField(default=1)

    # Relationships
    game_connections: ReverseRelation["PlayerGameConnection"]
    hosted_games: ReverseRelation["Game"]
    events: ReverseRelation["Event"]


class Game(BaseModel):
    """
    Represents a game.
    """

    class Status(str, Enum):
        IN_LOBBY = "LOBBY"
        IN_PROGRESS = "IN_PROGRESS"
        FINISHED = "FINISHED"
        ABORTED = "ABORTED"

    status = CharEnumField(Status, default=Status.IN_LOBBY, max_length=20)
    code = CharField(max_length=4, unique=True, default=generate_unique_game_code)

    # Relationships
    host = ForeignKeyField(
        "models.Player",
        related_name="hosted_games",
        null=True,
        on_delete=SET_NULL,
    )
    player_connections: ReverseRelation["PlayerGameConnection"]
    events: ReverseRelation["Event"]

    @property
    def is_in_lobby(self) -> bool:
        return self.status == Game.Status.IN_LOBBY

    @property
    def is_in_progress(self) -> bool:
        return self.status == Game.Status.IN_PROGRESS

    @property
    def is_finished(self) -> bool:
        return self.status in [Game.Status.FINISHED, Game.Status.ABORTED]

    async def add_player(self, player: Player) -> None:
        """Add a player to the game."""
        await PlayerGameConnection.create(player=player, game=self)

    async def set_host(self, player: Player) -> None:
        """Set the host of the game."""
        self.host = player


class PlayerGameConnection(BaseModel):
    """
    Represents a player's connection to a specific game.
    """

    last_heartbeat = DatetimeField(auto_now_add=True)
    activity_changed_at = DatetimeField(auto_now_add=True)
    is_active = BooleanField(default=True)

    # Relationships
    player = ForeignKeyField(
        "models.Player",
        related_name="connections",
        on_delete=CASCADE,
    )
    game = ForeignKeyField(
        "models.Game",
        related_name="connections",
        on_delete=CASCADE,
    )
    events: ReverseRelation["Event"]

    class Meta:
        unique_together = (("player", "game"),)

    @after_create
    async def create_player_joined_event(self):
        await Event.create(
            event_type=Event.Type.PLAYER_JOINED,
            game=self.game,
            player=self.player,
        )

    @after_update(fields=["is_active"])
    async def create_connection_event(self, previous: Self):
        if not previous.is_active and self.is_active:
            # Player reconnected
            await Event.create(
                event_type=Event.Type.PLAYER_RECONNECTED,
                game=self.game,
                player=self.player,
            )
        elif previous.is_active and not self.is_active:
            # Player disconnected
            await Event.create(
                event_type=Event.Type.PLAYER_DISCONNECTED,
                game=self.game,
                player=self.player,
            )


class Event(BaseModel):
    """
    Represents an event in the game (e.g., game started, player joined, etc.).
    """

    class Type(str, Enum):
        GAME_STARTED = "GAME_STARTED"
        GAME_FINISHED = "GAME_FINISHED"
        PLAYER_JOINED = "PLAYER_JOINED"
        PLAYER_DISCONNECTED = "PLAYER_DISCONNECTED"
        PLAYER_RECONNECTED = "PLAYER_RECONNECTED"

    event_type = CharEnumField(Type, max_length=20)

    # Relationships
    game = ForeignKeyField(
        "models.Game",
        related_name="events",
        on_delete=CASCADE,
    )
    player = ForeignKeyField(
        "models.Player",
        related_name="events",
        null=True,
        on_delete=SET_NULL,
    )
    connection = ForeignKeyField(
        "models.PlayerGameConnection",
        related_name="events",
        null=True,
        on_delete=SET_NULL,
    )


# # class Photo(BaseModel, table=True):
# #     """
# #     A photo uploaded by a player during a game.
# #     """
# #
# #     id: int | None = Field(default=None, primary_key=True)
# #     filename: str = Field(max_length=255, unique=True)
# #     original_filename: str | None = Field(default=None, max_length=255)
# #     is_roast_target: bool = Field(default=False)
# #     caption: str | None = Field(default=None, max_length=100)
# #
# #     turn_id: int | None = Field(default=None, foreign_key="turn.id")
# #     uploaded_by_id: int | None = Field(default=None, foreign_key="player.id")
# #
# #     # Relationships
# #     turn: Turn | None = Relationship(back_populates="photos")
# #     uploaded_by: Player | None = Relationship(back_populates="photos")
# #
# #     # Unique constraint
# #     __table_args__ = (UniqueConstraint("turn_id", "uploaded_by_id"),)
# #
# #     @property
# #     def file_path(self) -> str:
# #         """Get the full file path to the photo."""
# #         from main.config import settings
# #
# #         return str(settings.MEDIA_DIR / "photos" / self.filename)
# #
# #     @property
# #     def url(self) -> str:
# #         """Get the URL to access the photo."""
# #         return f"/media/photos/{self.filename}"
# #
# #     @property
# #     def exists(self) -> bool:
# #         """Check if the photo file exists on disk."""
# #         from pathlib import Path
# #
# #         return Path(self.file_path).exists()
#
#
# # class Roast(BaseModel, table=True):
# #     """
# #     Represents a roast generated by an LLM.
# #     """
# #
# #     id: int | None = Field(default=None, primary_key=True)
# #     text: str | None = Field(default=None)
# #     turn_id: int | None = Field(default=None, foreign_key="turn.id")
# #
# #     # Relationships
# #     turn: Turn | None = Relationship(back_populates="roasts")
# #     votes_received: list["Vote"] = Relationship(back_populates="roast")
# #
# #     @property
# #     def vote_count(self) -> int:
# #         return len(self.votes_received)
# #
# #     def is_already_voted_by(self, player: "Player") -> bool:
# #         return any(vote.submitted_by_id == player.id for vote in self.votes_received)
# #
# #
# # class Vote(SQLModel, table=True):
# #     """
# #     Represents a vote for a roast.
# #     """
# #
# #     id: int | None = Field(default=None, primary_key=True)
# #     roast_id: int | None = Field(default=None, foreign_key="roast.id")
# #     submitted_by_id: int | None = Field(default=None, foreign_key="player.id")
# #
# #     # Relationships
# #     roast: Roast | None = Relationship(back_populates="votes_received")
# #     submitted_by: Player | None = Relationship(back_populates="votes_submitted")
# #
# #     # Unique constraint
# #     __table_args__ = (UniqueConstraint("roast_id", "submitted_by_id"),)
