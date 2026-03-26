"""
Defines the database models for the 'games' app. These models represent the data structure
for game sessions, players, uploaded photos, and roasts.
"""
import base64
import time

import shortuuid
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Count
from django.utils import timezone

from main.games.enums import GameRoundState, GameState, HeatLevel


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


def generate_unique_code():
    """
    Generates a short, unique 4-character code using uppercase letters and numbers.
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    su = shortuuid.ShortUUID(alphabet=alphabet)
    return su.random(length=4)


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
        default=generate_unique_code,
        help_text='A unique 4-character game code for players to join.',
    )

    @property
    def number_of_rounds(self):
        return self.rounds.all().count()

    @property
    def round(self):
        return self.rounds.order_by('-count').first()

    @property
    def is_in_lobby(self):
        """Returns True if the game is in the lobby stage (round 0)."""
        return self.state == GameState.WAITING_FOR_PLAYERS

    @property
    def is_in_progress(self):
        """Returns True if the game is in progress (round > 0)."""
        return self.state == GameState.IN_PROGRESS

    def start_next_round(self) -> 'GameRound':
        """Creates a new round for this game."""
        return GameRound.objects.create(count=self.number_of_rounds + 1, game=self)

    def add_player(self, name, avatar, session_id) -> 'Player':
        """Creates a new player for this game."""
        return Player.objects.create(
            game=self, name=name, avatar=avatar, session_id=session_id
        )


class GameRound(BaseModel):
    """
    Represents a round in a game.
    """

    TIME_OFFSET = 2
    TIME_LIMITS = {
        GameRoundState.UPLOAD_PHOTO: 20 + TIME_OFFSET,
        GameRoundState.CHOOSE_ROAST_TARGET: 5 + TIME_OFFSET,
        GameRoundState.VOTE_ROAST_IDEAS: 60 + TIME_OFFSET,
        GameRoundState.SHOW_MOST_VOTED_IDEAS: 20 + TIME_OFFSET,
    }

    count = models.IntegerField(help_text='The game round number (1, 2, 3, etc.)')
    state = models.CharField(
        max_length=26,
        choices=GameRoundState.choices,
        default=GameRoundState.UPLOAD_PHOTO,
        help_text='Current state of this round.',
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')

    class Meta:
        unique_together = ['game', 'count']

    def clean(self):
        """
        Validates the game round instance before saving it to the database.
        """
        super().clean()

        if self.state == GameRoundState.CHOOSE_ROAST_TARGET:
            if not self.game.players.filter(photos__game_round=self).exists():
                msg = f'At least one player must upload a photo before proceeding to {self.state}.'
                raise ValidationError(msg)

    @property
    def seconds_left(self):
        """Calculate seconds left using the updated_at field."""
        time_limit = self.TIME_LIMITS[self.state]
        elapsed_time = timezone.now() - self.updated_at
        return max(0, time_limit - elapsed_time.seconds)

    @property
    def seconds_total(self):
        return self.TIME_LIMITS[self.state]

    @property
    def roast_target_photo(self):
        return self.photos.filter(is_roast_target=True).first()

    def choose_roast_target(self) -> 'Photo':
        """Selects a random photo from the uploaded photos."""
        photos = self.photos.all()

        photo = photos.order_by('?').first()
        photo.is_roast_target = True
        photo.save()

        return photo

    def add_roast_idea(self, text: str) -> 'RoastIdea':
        return RoastIdea.objects.create(
            game_round=self,
            text=text,
        )

    def add_roast_idea_vote(self, player: 'Player', roast_idea: 'RoastIdea') -> 'RoastIdeaVote':
        return RoastIdeaVote.objects.create(
            game_round=self,
            player=player,
            roast_idea=roast_idea,
        )

    def add_roast_poem(self, text: str) -> 'RoastPoem':
        """Creates the roast poem for this game round."""
        return RoastPoem.objects.create(
            game_round=self,
            photo=self.roast_target_photo,
            text=text,
        )

    def add_photo_for(self, player, cache_key):
        return Photo.objects.create(
            game_round=self, cache_key=cache_key, player=player
        )

    def photo_for(self, player: 'Player') -> 'Photo | None':
        """Returns the photo uploaded by the player for this round, if any."""
        return self.photos.filter(player=player).first()

    def get_most_voted_ideas(self):
        """Returns the top 10 roast ideas based on votes."""
        return self.roast_ideas.annotate(
            num_votes=Count('votes_received')
        ).order_by('-num_votes')[:5]

    def wait_for_players(self):
        time.sleep(self.TIME_LIMITS[self.state])


class Player(BaseModel):
    """
    Represents a player in a game.
    """

    session_id = models.CharField(
        max_length=32,
        help_text="Unique ID to track the player's browser session.",
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
        unique_together = ['game', 'session_id']

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
    player = models.ForeignKey(
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
        unique_together = ['game_round', 'player']

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


class RoastIdea(BaseModel):
    """
    Represents an idea of a roast generated by an LLM.
    """

    text = models.TextField(
        null=True,
        blank=True,
        help_text='The text of the roast contribution.',
    )
    roast_poem = models.ForeignKey(
        'RoastPoem',
        on_delete=models.CASCADE,
        related_name='roast_ideas',
        help_text='The roast poem this contribution belongs to.',
        null=True,
        blank=True,
    )
    game_round = models.ForeignKey(
        GameRound,
        on_delete=models.CASCADE,
        help_text='The round this roast contribution belongs to.',
        related_name='roast_ideas',
    )

    # Add a property to easily get the vote count
    @property
    def vote_count(self):
        # Access the related RoastIdeaVote objects via the 'votes_received' related_name
        return self.votes_received.count()

    def has_player_voted(self, player: Player) -> bool:
        return self.votes_received.filter(player=player).exists()


class RoastIdeaVote(models.Model):
    """
    Represents a single vote by a Player for a RoastIdea.
    Ensures a player can only vote once per idea.
    """
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='votes_cast',
        help_text='The player who cast this vote.'
    )
    roast_idea = models.ForeignKey(
        RoastIdea,
        on_delete=models.CASCADE,
        related_name='votes_received',  # Changed from 'votes' to avoid conflict
        help_text='The roast idea being voted for.'
    )
    game_round = models.ForeignKey(
        GameRound,
        on_delete=models.CASCADE,
        help_text='The round in which the vote was cast.',
        related_name='votes'    # Optional, but can be useful
    )

    class Meta:
        unique_together = ('player', 'roast_idea')


class RoastPoem(BaseModel):
    """
    Represents the roast poem generated from player contributions.
    """

    text = models.TextField(
        null=True,
        blank=True,
        help_text='The final text of the completed roast.',
    )
    game_round = models.OneToOneField(
        GameRound,
        on_delete=models.CASCADE,
        help_text='The game round this roast belongs to.',
        related_name='roast_poem',
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        help_text='The photo being roasted.',
    )
