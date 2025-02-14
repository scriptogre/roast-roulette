"""
Defines the database models for the 'games' app. These models represent the data structure
for game sessions, players, uploaded photos, and roasts/clapbacks.
"""

import shortuuid
from django.core.validators import MinLengthValidator
from django.db import models


def generate_unique_code():
    """Generates a short, unique 4-character code using uppercase letters and numbers."""
    # Custom alphabet with uppercase letters and digits
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    su = shortuuid.ShortUUID(alphabet=alphabet)
    return su.random(length=4)


class Game(models.Model):
    """
    Represents a game session.
    """

    code = models.CharField(
        max_length=4,
        unique=True,
        default=generate_unique_code,
        help_text='A unique 4-character game code for players to join.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp of game creation.',
    )
    current_round = models.IntegerField(
        default=0,
        help_text='Tracks which round the game is in.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indicates if the game is ongoing or ended.',
    )

    def add_player(self, name, avatar, session_id):
        """Creates a new player for this game."""
        return Player.objects.create(
            game=self, name=name, avatar=avatar, session_id=session_id
        )

    def add_photo(self, player, image):
        """Adds a photo uploaded by a player to the game."""
        # TODO: Should also track for which round the photo was uploaded
        return Photo.objects.create(game=self, player=player, image=image)

    @property
    def players(self):
        """Returns all players in this game."""
        return Player.objects.filter(game=self)


class Player(models.Model):
    """
    Represents a player in a game.
    """

    name = models.CharField(
        max_length=50,
        help_text="The player's display name.",
        validators=[MinLengthValidator(3)],
    )
    session_id = models.CharField(
        max_length=32,
        help_text="Unique ID to track the player's browser session.",
    )
    score = models.IntegerField(
        default=0,
        help_text="The player's score.",
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=True,
        help_text='The game this player belongs to.',
    )
    is_host = models.BooleanField(
        default=False,
        help_text='True if the player created the game.',
    )
    avatar = models.IntegerField(
        choices=[(i, i) for i in range(1, 9)],
        default=1,
        help_text="Number representing the player's chosen avatar (1-8).",
    )

    class Meta:
        unique_together = ['game', 'session_id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Photo(models.Model):
    """
    A photo uploaded by a player during a game.
    """

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        help_text='The game this photo belongs to.',
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        help_text='The player who uploaded the photo.',
    )
    image = models.ImageField(
        upload_to='uploads/',
        help_text='The uploaded image file.',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp of photo upload.',
    )
    round_number = models.IntegerField(
        default=0,
        help_text='The round number for this photo.',
    )


class Roast(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        help_text='The game this roast belongs to.',
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        help_text='The photo being roasted.',
    )
    ai_roast = models.TextField(
        help_text='The AI-generated roast for this photo.',
    )
    clapback = models.TextField(
        blank=True,
        help_text="Player's witty response to the roast.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp of roast creation.',
    )
