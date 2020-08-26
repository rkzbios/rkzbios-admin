"""Command for sending the newsletter"""
from django.core.management.base import NoArgsCommand

from ...services_org import batch_mailer



class Command(NoArgsCommand):
    """Send the newsletter in queue"""
    help = 'Send the newsletter in queue'

    def handle_noargs(self, **options):
        verbose = int(options['verbosity'])
        site_id = options['site_id'] if 'site_id' in options else 1

        if verbose:
            print 'Starting retrieving bounces...'

        batch_mailer.reconciliate_bounces(site_id)
        
        if verbose:
            print 'End retrieving bounces'
