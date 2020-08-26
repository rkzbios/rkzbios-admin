"""Command for sending the newsletter"""
from django.core.management.base import BaseCommand

from ...services import mail_service



class Command(BaseCommand):
    """Send the newsletter in queue"""
    help = 'Send the mail in queue'

    def handle(self, **options):
        verbose = int(options['verbosity'])

        if verbose:
            print('Starting sending mail...')

        mail_service.run()
        
        if verbose:
            print('End session sending')
