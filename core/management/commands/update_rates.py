from django.core.management.base import BaseCommand

from core.services.rate_updater import fetch_and_update_rates


class Command(BaseCommand):
    help = 'Fetch latest exchange rates from the Frankfurter API and update the database.'

    def handle(self, *args, **options):
        self.stdout.write('Fetching exchange rates...')
        fetch_and_update_rates()
        self.stdout.write(self.style.SUCCESS('Done.'))
