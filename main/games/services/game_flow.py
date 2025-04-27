import asyncio

from main.games.consumers import trigger_clients_refresh
from main.games.enums import GameRoundStage, GameState
from main.games.models import GameRound, Game
from main.games.services.crud import get_random_photo
from main.games.services.generation import generate_roasts


async def play_game_round_in_background(game: Game, game_round: GameRound):
    """Async state progression with explicit steps"""

    """1. Upload photo"""
    game_round.stage = GameRoundStage.UPLOAD_PHOTO
    await game_round.asave()

    await trigger_clients_refresh(game.code)

    try:
        async with asyncio.timeout(GameRound.TIME_LIMITS[GameRoundStage.UPLOAD_PHOTO]):
            while not await game_round.photos.aexists():
                await asyncio.sleep(1)
    except TimeoutError:
        # Timeout reached, abort the round
        game.rounds.filter(id=game_round.id).delete()
        await trigger_clients_refresh(game_round.game.code)
        return

    """
    2. Wait for roast roulette
    """
    # Get random photo
    target_photo = await get_random_photo(game_round=game_round)
    target_photo.is_roast_target = True
    await target_photo.asave()

    for text in await generate_roasts(photo=target_photo):
        await game_round.roasts.acreate(text=text)

    game_round.stage = GameRoundStage.WAIT_FOR_ROULETTE
    await game_round.asave()
    await trigger_clients_refresh(game.code)

    # Wait for roulette animation
    await asyncio.sleep(game_round.stage_seconds_total)

    """
    3. Vote for roast ideas
    """
    game_round.stage = GameRoundStage.VOTE_ROASTS
    await game_round.asave()
    await trigger_clients_refresh(game.code)

    # Wait for votes
    await asyncio.sleep(GameRound.TIME_LIMITS[GameRoundStage.VOTE_ROASTS])

    """
    4. Show best roasts
    """
    game_round.stage = GameRoundStage.SHOW_RESULTS
    await game_round.asave()
    await trigger_clients_refresh(game.code)

#
# def clean(self):
#     """
#     Validates the game round instance before saving it to the database.
#     """
#     super().clean()
#
#     if self.stage == GameRoundStage.CHOOSE_ROAST_TARGET:
#         if not self.game.players.filter(photos__game_round=self).exists():
#             msg = f'At least one player must upload a photo before proceeding to {self.stage}.'
#             raise ValidationError(msg)

# def choose_roast_target(self) -> 'Photo':
#     """Selects a random photo from the uploaded photos."""
#     photos = self.photos.all()
#
#     photo = photos.order_by('?').first()
#     photo.is_roast_target = True
#     photo.save()
#
#     return photo


# # --- UPLOAD PHOTO ---
# game_round.state = GameRoundStage.UPLOAD_PHOTO
# game_round.save()
# trigger_clients_refresh(game_code)
# game_round.wait_for_players()
#
# # Abort if no photos uploaded
# if not game_round.photos.exists():
#     game.rounds.filter(id=game_round.id).delete()
#     trigger_clients_refresh(game_code)
#     return HttpResponse('No photos uploaded, cannot continue round.', status=400)
#
# roast_target_photo = game_round.choose_roast_target()
#
# future = generate_roasts_in_the_background(
#     roast_target_photo,
#     count=20,
# )
#
# # --- CHOOSE ROAST TARGET (ROULETTE) ---
# game_round.state = GameRoundStage.CHOOSE_ROAST_TARGET
# game_round.save()
# trigger_clients_refresh(game_code)
# game_round.wait_for_players()
#
# generated_roasts = future.result()
# for text in generated_roasts:
# RoastIdea.objects.create(
#             game_round=game_round,
#             text=text,
#         )
#
# # --- VOTE ROAST IDEAS ---
# game_round.state = GameRoundStage.VOTE_roastS
# game_round.save()
# trigger_clients_refresh(game_code)
# game_round.wait_for_players()
#
# future = generate_roast_poem_in_the_background(
#     roast_target_photo,
#     roasts=[idea.text for idea in game_round.roasts.all()],
# )
#
# # -- SHOW MOST VOTED IDEAS --
# game_round.state = GameRoundStage.SHOW_MOST_VOTED_IDEAS
# game_round.save()
# trigger_clients_refresh(game_code)
# game_round.wait_for_players()
#
# # Create the roast ideas
# generated_poem_text = future.result()
# game_round.add_roast_poem(generated_poem_text)
# RoastPoem.objects.create(
#             game_round=self,
#             photo=self.roast_target_photo,
#             text=text,
#         )
#
# # --- SHOW ROAST POEM ---
# game_round.state = GameRoundStage.SHOW_ROAST_POEM
# game_round.save()
# trigger_clients_refresh(game_code)
#


