import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, ComparisonTheme, ComparisonEntry


class Command(BaseCommand):
    help = "Load comparison themes mapping doctrinal topics across all three standards"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "comparison_themes.json"
        if data_is_current("comparison-themes", data_path):
            self.stdout.write("Comparison themes unchanged, skipping.")
            return

        catechisms = {c.slug: c for c in Catechism.objects.all()}
        with open(data_path) as f:
            data = json.load(f)

        theme_count = 0
        entry_count = 0
        loaded_slugs = set()

        for item in data:
            theme, _ = ComparisonTheme.objects.update_or_create(
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
                    ComparisonEntry.objects.filter(
                        theme=theme, catechism=catechisms[cat_slug]
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

        deleted_count, _ = ComparisonTheme.objects.exclude(
            slug__in=loaded_slugs
        ).delete()
        if deleted_count:
            self.stdout.write(f"Removed {deleted_count} orphaned theme(s)")

        mark_data_current("comparison-themes", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {theme_count} comparison themes with {entry_count} new entries"
        ))
