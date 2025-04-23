from django.conf import settings
from django.contrib.staticfiles.finders import AppDirectoriesFinder


class CustomAppDirectoriesFinder(AppDirectoriesFinder):
    def list(self, ignore_patterns=None):
        # Combine default ignore patterns with custom ones from settings
        custom_ignore_patterns = getattr(settings, 'STATICFILES_IGNORE', [])
        ignore_patterns = (ignore_patterns or []) + custom_ignore_patterns
        return super().list(ignore_patterns)
