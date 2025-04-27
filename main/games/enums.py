from django.db.models import TextChoices


class GameState(TextChoices):
    WAITING_FOR_PLAYERS = 'WAITING_FOR_PLAYERS', 'Waiting for Players'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    FINISHED = 'FINISHED', 'Finished'
    ABORTED = 'ABORTED', 'Aborted'


class GameRoundStage(TextChoices):
    UPLOAD_PHOTO = 'UPLOAD_PHOTO', 'Uploading photos...'
    WAIT_FOR_ROULETTE = 'WAIT_FOR_ROULETTE', 'Spinning the roast roulette...'
    VOTE_ROASTS = 'VOTE_ROASTS', 'Voting roast ideas...'
    SHOW_RESULTS = 'SHOW_RESULTS', 'Showing most voted ideas...'
