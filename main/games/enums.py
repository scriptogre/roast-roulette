from django.db.models import TextChoices


class HeatLevel(TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'

    @property
    def description(self):
        """User-facing description."""
        return {
            self.LOW: 'Just a light roast.',
            self.MEDIUM: 'Land a few punches.',
            self.HIGH: 'Have no mercy.',
        }.get(self)

    @property
    def instructions_for_llm(self):
        """Instructions specifically for the AI."""
        return {
            self.LOW: 'Generate mild, playful roasts. Avoid anything genuinely harsh or offensive.',
            self.MEDIUM: 'Generate standard witty roasts. Clever burns are good, but avoid excessively mean-spirited content.',
            self.HIGH: 'Generate sharp, ruthless roasts. The user wants high intensity, but still aim for creativity over pure insult.',
        }.get(self)


class GameState(TextChoices):
    WAITING_FOR_PLAYERS = 'WAITING_FOR_PLAYERS', 'Waiting for Players'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    FINISHED = 'FINISHED', 'Finished'
    ABORTED = 'ABORTED', 'Aborted'


class GameRoundState(TextChoices):
    UPLOAD_PHOTO = 'UPLOAD_PHOTO', 'Upload Photo'
    CHOOSE_ROAST_TARGET = (
        'CHOOSE_ROAST_TARGET',
        'Choose Roast Target',
    )
    VOTE_ROAST_IDEAS = 'VOTE_ROAST_IDEAS', 'Vote Roast Ideas'
    SHOW_MOST_VOTED_IDEAS = (
        'SHOW_MOST_VOTED_IDEAS',
        'Show Most Voted Ideas',
    )
    SHOW_ROAST_POEM = 'SHOW_ROAST_POEM', 'Show Roast Poem'

    @property
    def instructions(self):
        return {
            self.UPLOAD_PHOTO: 'Uploading photos...',
            self.CHOOSE_ROAST_TARGET: 'Choosing roast target...',
            self.VOTE_ROAST_IDEAS: 'Voting roast ideas...',
            self.SHOW_MOST_VOTED_IDEAS: 'Showing most voted ideas...',
            self.SHOW_ROAST_POEM: 'Game round finished!',
        }.get(self)
