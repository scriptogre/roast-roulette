from uuid import uuid4

from django.core.cache import cache

from main.games.enums import GameState
from main.games.models import GameRound, Photo, Game, Roast, Vote, Player


# --- CREATE ---


async def create_game() -> Game:
    return await Game.objects.acreate()


async def create_game_round(*, game: Game) -> GameRound:
    game.state = GameState.IN_PROGRESS
    await game.asave()

    return await game.rounds.acreate(count=await game.rounds.acount() + 1)


async def create_player(
    *, game: Game, player_name: str, avatar: str, session_key: str
) -> Player:
    return await Player.objects.acreate(
        game=game,
        name=player_name,
        avatar=avatar,
        session_key=session_key
    )


async def create_host_player(
    *, game: Game, player_name: str, avatar: str, session_key: str
) -> Player:
    return await Player.objects.acreate(
        game=game,
        name=player_name,
        avatar=avatar,
        session_key=session_key,
        is_host=True
    )


async def create_photo(game_round: GameRound, player: Player, uploaded_file) -> Photo:
    """
    Handle caching the uploaded photo content and creating a Photo record.
    """
    cache_key = f'photo:{uuid4()}'
    cache.set(cache_key, uploaded_file.read(), timeout=3600)
    return await Photo.objects.acreate(
        game_round=game_round,
        cache_key=cache_key,
        uploaded_by=player,
    )


async def create_vote(*, roast: Roast, submitted_by: Player) -> Vote:
    return await Vote.objects.acreate(roast=roast, submitted_by=submitted_by)


# --- READ ---


async def get_game_by_code(*, code: str) -> Game | None:
    return await Game.objects.filter(code=code.upper()).afirst()


async def get_current_game_round(*, game: Game) -> GameRound | None:
    return await game.rounds.order_by('-count').afirst()


async def get_player_by_session(*, game: Game, session_key: str) -> Player | None:
    return await game.players.filter(session_key=session_key).afirst()


async def get_host_player(*, game: Game) -> Player | None:
    return await game.players.filter(is_host=True).afirst()


async def get_players(*, game: Game) -> list[Player]:
    return [player async for player in game.players.all()]


async def get_photos(*, game_round: GameRound) -> list[Photo]:
    return [photo async for photo in game_round.photos.select_related('uploaded_by')]


async def get_target_photo(*, game_round: GameRound) -> Photo | None:
    return await game_round.photos.filter(is_roast_target=True).select_related('uploaded_by').afirst()

async def get_random_photo(*, game_round: GameRound) -> Photo | None:
    return await game_round.photos.order_by('?').afirst()

async def get_roasts(*, game_round: GameRound) -> list[Roast]:
    return [roast async for roast in Roast.objects.filter(game_round=game_round)]


async def get_roast_by_id(*, game_round: GameRound, roast_id: str) -> Roast:
    return await game_round.roasts.aget(id=roast_id)


async def get_photo_uploaded_by_player(*, game_round: GameRound, player: Player) -> Photo | None:
    return await game_round.photos.filter(uploaded_by=player).afirst()


async def get_vote_by_id(*, roast: Roast, submitted_by: Player, vote_id: str) -> Vote:
    return await roast.votes_received.aget(id=vote_id, submitted_by=submitted_by)


# --- DELETE ---


async def delete_vote(*, vote: Vote):
    return await vote.adelete()
