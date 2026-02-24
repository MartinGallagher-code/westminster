from django.core.management.base import BaseCommand

from catechism.models import CommentarySource

ACTIVE_SLUGS = [
    'fisher-erskine', 'flavel', 'henry', 'watson',
    'vincent', 'ridgley', 'shaw', 'hodge',
]


class Command(BaseCommand):
    help = "Remove commentary sources not in the active set"

    def handle(self, *args, **options):
        deleted, _ = CommentarySource.objects.exclude(slug__in=ACTIVE_SLUGS).delete()
        if deleted:
            self.stdout.write(f'Deleted {deleted} stale commentary record(s)')
        else:
            self.stdout.write('No stale sources found')
