# Generated by Django 5.1.7 on 2025-04-28 21:21

import django.core.validators
import django.db.models.deletion
import main.games.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time this record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time this record was last updated.')),
                ('state', models.CharField(choices=[('WAITING_FOR_PLAYERS', 'Waiting for Players'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished'), ('ABORTED', 'Aborted')], default='WAITING_FOR_PLAYERS', help_text='Current state of this game.', max_length=26)),
                ('code', models.CharField(default=main.games.utils.generate_unique_game_code, help_text='A unique 4-character game code for players to join.', max_length=4, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GameRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time this record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time this record was last updated.')),
                ('count', models.IntegerField(help_text='The game round number (1, 2, 3, etc.)')),
                ('stage', models.CharField(choices=[('UPLOAD_PHOTO', 'Uploading photos...'), ('WAIT_FOR_ROULETTE', 'Spinning the roast roulette...'), ('VOTE_ROASTS', 'Voting roast ideas...'), ('SHOW_RESULTS', 'Showing most voted ideas...')], default='UPLOAD_PHOTO', help_text='Current stage of this round.', max_length=26)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='games.game')),
            ],
            options={
                'unique_together': {('game', 'count')},
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time this record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time this record was last updated.')),
                ('session_key', models.CharField(help_text="Unique key to track the player's browser session.", max_length=32)),
                ('name', models.CharField(help_text="The player's display name.", max_length=32, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(32)])),
                ('avatar', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], default=1, help_text="Number representing the player's chosen avatar (1-8).")),
                ('is_host', models.BooleanField(default=False, help_text='True if the player created the game.')),
                ('game', models.ForeignKey(help_text='The game this player belongs to.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='games.game')),
            ],
            options={
                'unique_together': {('game', 'session_key')},
            },
        ),
        migrations.CreateModel(
            name='Roast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time this record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time this record was last updated.')),
                ('text', models.TextField(blank=True, help_text='The text of the roast.', null=True)),
                ('game_round', models.ForeignKey(help_text='The round this roast contribution belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='roasts', to='games.gameround')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time this record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The date and time this record was last updated.')),
                ('cache_key', models.CharField(help_text='Key for the image data in Redis', max_length=255, unique=True)),
                ('is_roast_target', models.BooleanField(default=False, help_text='True if this photo is the target for roasting in the current game round.')),
                ('caption', models.CharField(blank=True, help_text='The caption for the photo.', max_length=100, null=True, validators=[django.core.validators.MaxLengthValidator(100)])),
                ('game_round', models.ForeignKey(help_text='The game round this photo belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='games.gameround')),
                ('uploaded_by', models.ForeignKey(help_text='The player who uploaded the photo.', on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='games.player')),
            ],
            options={
                'unique_together': {('game_round', 'uploaded_by')},
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roast', models.ForeignKey(help_text='The roast receiving the vote.', on_delete=django.db.models.deletion.CASCADE, related_name='votes_received', to='games.roast')),
                ('submitted_by', models.ForeignKey(help_text='The player who submitted this vote.', on_delete=django.db.models.deletion.CASCADE, related_name='votes_submitted', to='games.player')),
            ],
            options={
                'unique_together': {('roast', 'submitted_by')},
            },
        ),
    ]
