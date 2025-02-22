"""
Defines the database models for the 'games' app. These models represent the data structure
for game sessions, players, uploaded photos, and roasts.
"""

import time

import shortuuid
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import TextChoices
from django.utils import timezone


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

    code = models.CharField(
        max_length=4,
        unique=True,
        default=generate_unique_code,
        help_text='A unique 4-character game code for players to join.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indicates if the game is ongoing or ended.',
    )

    @property
    def number_of_rounds(self):
        return self.rounds.all().count()

    @property
    def current_round(self):
        if self.number_of_rounds == 0:
            return None

        return self.rounds.get(count=self.number_of_rounds)

    @property
    def is_lobby(self):
        """Returns True if the game is in the lobby stage (round 0)."""
        return self.number_of_rounds == 0

    def start_round(self):
        """Creates a new round for this game."""
        return Round.objects.create(count=self.number_of_rounds + 1, game=self)

    def add_player(self, name, avatar, session_id):
        """Creates a new player for this game."""
        return Player.objects.create(
            game=self, name=name, avatar=avatar, session_id=session_id
        )


class Round(BaseModel):
    """
    Represents a round in a game.
    """

    class State(TextChoices):
        SUBMIT_PHOTOS = 'SUBMIT_PHOTOS', 'Submit Photos'
        SHOW_TARGET = 'SHOW_TARGET', 'Show Roast Target Photo'
        SUBMIT_ROASTS = 'SUBMIT_ROASTS', 'Submit Roasts for Target Photo'
        SHOW_ROAST = 'SHOW_ROAST', 'Show Roast'

    TIME_LIMITS = {
        State.SUBMIT_PHOTOS: 60,
        State.SHOW_TARGET: 10,
        State.SUBMIT_ROASTS: 180,
        State.SHOW_ROAST: 30,
    }

    count = models.IntegerField(help_text='The round number (1, 2, 3, etc.)')
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.SUBMIT_PHOTOS,
        help_text='Current state of this round.',
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')

    class Meta:
        unique_together = ['game', 'count']

    def clean(self):
        """
        Validates the round instance before saving it to the database.
        """
        super().clean()

        if self.state == self.State.SHOW_TARGET:
            all_players_uploaded = (
                self.game.players.filter(photos__round=self).count()
                == self.game.players.count()
            )
            if not all_players_uploaded:
                msg = (
                    f'All players must upload photos before proceeding to {self.state}.'
                )
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
    def target_photo(self):
        return self.photos.filter(is_roast_target=True).first()

    def pick_target_photo(self):
        """Selects a random photo from the uploaded photos."""
        photos = self.photos.all()

        target_photo = photos.order_by('?').first()
        target_photo.is_roast_target = True
        target_photo.save()

        return target_photo

    def wait_for_players(self):
        """Waits for players to submit roast pieces."""
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
    hp = models.IntegerField(
        default=3,
        help_text="The player's health points.",
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

    @property
    def photo(self):
        return self.photos.filter(round=self.game.current_round).first()

    @property
    def roast_pieces(self):
        return self.roast_pieces.filter(round=self.game.current_round)

    def add_photo(self, image):
        """Creates a new photo for this player."""
        return Photo.objects.create(
            image=image, round=self.game.current_round, player=self
        )

    def add_roast_pieces(self, snippets: list[str]):
        """Creates roast pieces for this player."""
        for snippet in snippets:
            RoastPieces.objects.create(
                player=self,
                round=self.game.current_round,
                game=self.game,
                text=snippet,
            )


class Photo(BaseModel):
    """
    A photo uploaded by a player during a game.
    """

    image = models.ImageField(
        upload_to='uploads/',
        help_text='The uploaded image file.',
    )
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        help_text='The round this photo belongs to.',
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
        help_text='True if this photo is the target for roasting in the current round.',
    )

    class Meta:
        unique_together = ['round', 'player']

    def clean(self):
        super().clean()

        # Ensure photo is smaller than 10MB
        if self.image.size > 10 * 1024 * 1024:
            raise ValidationError('Image file size must be less than 10MB.')


class Roast(BaseModel):
    """
    Represents a roast for a photo.
    """

    round = models.OneToOneField(
        Round,
        on_delete=models.CASCADE,
        help_text='The round this roast belongs to.',
        related_name='roast',
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        help_text='The photo being roasted.',
    )
    roast_text = models.TextField(
        null=True,
        blank=True,
        help_text='The final composed roast text.',
    )


class RoastPieces(BaseModel):
    roast = models.ForeignKey(
        Roast,
        on_delete=models.CASCADE,
        related_name='pieces',
        help_text='The roast this roast piece belongs to.',
        null=True,
        blank=True,
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        help_text='The player who contributed the roast piece.',
        related_name='roast_pieces',
    )
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        help_text='The round this roast piece belongs to.',
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        help_text='The game this roast piece belongs to.',
    )
    text = models.TextField(help_text='A single roast piece.')
