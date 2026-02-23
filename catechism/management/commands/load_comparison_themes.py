import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, ComparisonSet, ComparisonTheme, ComparisonEntry

COMPARISON_SETS = {
    'westminster': {
        'name': 'Westminster Standards',
        'description': (
            'Compare doctrinal themes side-by-side across the Westminster '
            'Shorter Catechism, Larger Catechism, and Confession of Faith.'
        ),
        'order': 1,
        'file': 'comparison_themes.json',
        'data_version_key': 'comparison-themes',
    },
    'three-forms': {
        'name': 'Three Forms of Unity',
        'description': (
            'Compare doctrinal themes across the Heidelberg Catechism, '
            'Belgic Confession, and Canons of Dort — the confessional '
            'standards of the Continental Reformed churches.'
        ),
        'order': 2,
        'file': 'comparison_themes_tfu.json',
        'data_version_key': 'comparison-themes-tfu',
    },
    '1689-baptist': {
        'name': 'Confessional Lineage: Westminster to Baptist',
        'description': (
            'Compare the Westminster Confession of Faith (1646), the '
            'Savoy Declaration (1658), and the 1689 London Baptist '
            'Confession side-by-side, tracing the evolution of Reformed '
            'confessional theology from Presbyterian to Congregationalist '
            'to Baptist polity.'
        ),
        'order': 3,
        'file': 'comparison_themes_1689.json',
        'data_version_key': 'comparison-themes-1689',
    },
    'pre-westminster': {
        'name': 'Pre-Westminster Confessions',
        'description': (
            'Compare the Westminster Confession with its historical '
            'predecessors: the Scots Confession (1560), Second Helvetic '
            'Confession (1566), and Irish Articles of Religion (1615) — '
            'documents that shaped the Westminster Assembly\'s work.'
        ),
        'order': 4,
        'file': 'comparison_themes_pre_westminster.json',
        'data_version_key': 'comparison-themes-pre-westminster',
    },
}


class Command(BaseCommand):
    help = "Load comparison themes mapping doctrinal topics across standards"

    def add_arguments(self, parser):
        parser.add_argument(
            '--set',
            type=str,
            default='westminster',
            choices=COMPARISON_SETS.keys(),
            help='Which comparison set to load (default: westminster)',
        )

    def handle(self, *args, **options):
        set_slug = options['set']
        set_config = COMPARISON_SETS[set_slug]

        data_path = settings.BASE_DIR / "data" / set_config['file']
        version_key = set_config['data_version_key']

        if data_is_current(version_key, data_path):
            self.stdout.write(f"{set_config['name']} themes unchanged, skipping.")
            return

        # Get or create the ComparisonSet
        comparison_set, _ = ComparisonSet.objects.update_or_create(
            slug=set_slug,
            defaults={
                'name': set_config['name'],
                'description': set_config['description'],
                'order': set_config['order'],
            },
        )

        catechisms = {c.slug: c for c in Catechism.objects.all()}
        with open(data_path) as f:
            data = json.load(f)

        theme_count = 0
        entry_count = 0
        loaded_slugs = set()

        for item in data:
            theme, _ = ComparisonTheme.objects.update_or_create(
                comparison_set=comparison_set,
                slug=item['slug'],
                defaults={
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'locus': item.get('locus', ''),
                    'order': item['order'],
                }
            )
            loaded_slugs.add(item['slug'])
            theme_count += 1

            for cat_slug, range_pair in item.get('entries', {}).items():
                if range_pair is None:
                    cat = catechisms.get(cat_slug)
                    if cat:
                        ComparisonEntry.objects.filter(
                            theme=theme, catechism=cat
                        ).delete()
                    continue

                cat = catechisms.get(cat_slug)
                if not cat:
                    self.stderr.write(f"Catechism '{cat_slug}' not found, skipping")
                    continue

                _, created = ComparisonEntry.objects.update_or_create(
                    theme=theme,
                    catechism=cat,
                    defaults={
                        'question_start': range_pair[0],
                        'question_end': range_pair[1],
                    }
                )
                if created:
                    entry_count += 1

        # Only delete orphaned themes within this comparison set
        deleted_count, _ = ComparisonTheme.objects.filter(
            comparison_set=comparison_set
        ).exclude(
            slug__in=loaded_slugs
        ).delete()
        if deleted_count:
            self.stdout.write(f"Removed {deleted_count} orphaned theme(s)")

        mark_data_current(version_key, data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {theme_count} {set_config['name']} themes with {entry_count} new entries"
        ))
