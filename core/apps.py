import os
import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # In Django's dev server the auto-reloader forks a child process with
        # RUN_MAIN=true.  We only start the scheduler in that child (the actual
        # server), not in the parent watcher process, to avoid running it twice.
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return

        from core.scheduler import start_scheduler
        start_scheduler()
