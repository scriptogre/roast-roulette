"""
Defines the database models for the 'games' app. These models represent the data structure
for game sessions, players, uploaded photos, and roasts.
"""
import base64

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Count
from django.utils import timezone

from main.games.enums import GameRoundStage, GameState
from main.games.utils import generate_unique_game_code


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The date and time this record was created.',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='The date and time this record was last updated.',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Validates the model instance before saving it to the database.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class Game(BaseModel):
    """
    Represents a game session.
    """

    state = models.CharField(
        max_length=26,
        choices=GameState.choices,
        default=GameState.WAITING_FOR_PLAYERS,
        help_text='Current state of this game.',
    )
    code = models.CharField(
        max_length=4,
        unique=True,
        default=generate_unique_game_code,
        help_text='A unique 4-character game code for players to join.',
    )

    @property
    def is_in_lobby(self):
        return self.state == GameState.WAITING_FOR_PLAYERS

    @property
    def is_in_progress(self):
        return self.state == GameState.IN_PROGRESS


class GameRound(BaseModel):
    """
    Represents a round in a game.
    """
    TIME_LIMITS = {
        GameRoundStage.UPLOAD_PHOTO: 60,
        GameRoundStage.WAIT_FOR_ROULETTE: 10,
        GameRoundStage.VOTE_ROASTS: 60,
        GameRoundStage.SHOW_RESULTS: 60,
    }

    count = models.IntegerField(help_text='The game round number (1, 2, 3, etc.)')
    stage = models.CharField(
        max_length=26,
        choices=GameRoundStage.choices,
        default=GameRoundStage.UPLOAD_PHOTO,
        help_text='Current stage of this round.',
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')

    class Meta:
        unique_together = ['game', 'count']

    @property
    def stage_seconds_total(self) -> int:
        return self.TIME_LIMITS.get(self.stage, 0)

    @property
    def stage_seconds_left(self):
        elapsed_time = timezone.now() - self.updated_at
        return max(0, self.stage_seconds_total - elapsed_time.seconds)

    @property
    def is_finished(self):
        return self.stage == GameRoundStage.SHOW_RESULTS

    def get_top_roasts(self):
        """Returns the top 5 roasts based on votes."""
        return self.roasts.annotate(
            vote_count=Count('votes_received')
        ).order_by('-vote_count')[:5]


class Player(BaseModel):
    """
    Represents a player in a game.
    """

    session_key = models.CharField(
        max_length=32,
        help_text="Unique key to track the player's browser session.",
    )
    name = models.CharField(
        max_length=32,
        help_text="The player's display name.",
        validators=[MinLengthValidator(3), MaxLengthValidator(32)],
    )
    avatar = models.IntegerField(
        choices=[(i, i) for i in range(1, 9)],
        default=1,
        help_text="Number representing the player's chosen avatar (1-8).",
    )
    is_host = models.BooleanField(
        default=False,
        help_text='True if the player created the game.',
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=True,
        help_text='The game this player belongs to.',
        related_name='players',
    )

    class Meta:
        unique_together = ['game', 'session_key']

    def clean(self, *args, **kwargs):
        super().clean()

        # Ensure player name is unique in the game
        if self.game.players.filter(name=self.name).exclude(id=self.id).exists():
            raise ValidationError(
                {'name': 'This player name is already taken in this game.'},
                code='player_name_taken',
            )


class Photo(BaseModel):
    """
    A photo uploaded by a player during a game.
    """
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        help_text='Key for the image data in Redis'
    )
    game_round = models.ForeignKey(
        GameRound,
        on_delete=models.CASCADE,
        help_text='The game round this photo belongs to.',
        related_name='photos',
    )
    uploaded_by = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        help_text='The player who uploaded the photo.',
        related_name='photos',
    )
    is_roast_target = models.BooleanField(
        default=False,
        help_text='True if this photo is the target for roasting in the current game round.',
    )
    caption = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='The caption for the photo.',
        validators=[MaxLengthValidator(100)],
    )

    class Meta:
        unique_together = ['game_round', 'uploaded_by']

    @property
    def base64_url(self):
        """Generate a base64 URL for the image."""
        from django.core.cache import cache

        # Determine content type
        content_type = 'image/png' if self.cache_key.lower().endswith('.png') else 'image/jpeg'

        # Get binary image data and encode it to base64
        binary_image = cache.get(self.cache_key) or b''
        base64_image = base64.b64encode(binary_image).decode('utf-8') if binary_image else ""

        return f'data:{content_type};base64,{base64_image}' if binary_image else ""


class Roast(BaseModel):
    """
    Represents a roast generated by an LLM.
    """

    text = models.TextField(
        null=True,
        blank=True,
        help_text='The text of the roast.',
    )
    game_round = models.ForeignKey(
        GameRound,
        on_delete=models.CASCADE,
        help_text='The round this roast contribution belongs to.',
        related_name='roasts',
    )

    @property
    async def vote_count(self):
        return await self.votes_received.acount()

    def is_already_voted_by(self, player: Player) -> bool:
        return self.votes_received.filter(player=player).exists()


class Vote(models.Model):
    roast = models.ForeignKey(
        Roast,
        on_delete=models.CASCADE,
        related_name='votes_received',
        help_text='The roast receiving the vote.'
    )
    submitted_by = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='votes_submitted',
        help_text='The player who submitted this vote.'
    )

    class Meta:
        unique_together = ('roast', 'submitted_by')
