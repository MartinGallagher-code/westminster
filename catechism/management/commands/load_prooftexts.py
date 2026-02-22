import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Question


class Command(BaseCommand):
    help = "Load proof text references into Question records"

    def add_arguments(self, parser):
        parser.add_argument(
            '--catechism', type=str, default='wsc',
            help='Catechism slug (default: wsc)'
        )

    def handle(self, *args, **options):
        cat_slug = options['catechism']
        catechism = Catechism.objects.get(slug=cat_slug)

        filename = 'proof_texts.json' if cat_slug == 'wsc' else f'{cat_slug}_proof_texts.json'
        data_path = settings.BASE_DIR / "data" / filename
        if not data_path.exists():
            self.stderr.write(self.style.WARNING(
                f"Proof texts file not found: {data_path}. Skipping."
            ))
            return

        version_name = f"prooftexts-{cat_slug}"
        if data_is_current(version_name, data_path):
            self.stdout.write(f"{catechism.abbreviation} proof texts unchanged, skipping.")
            return

        with open(data_path) as f:
            proof_data = json.load(f)

        updated = 0
        for num_str, refs in proof_data.items():
            count = Question.objects.filter(
                catechism=catechism, number=int(num_str)
            ).update(proof_texts=refs)
            updated += count

        mark_data_current(version_name, data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Updated proof texts for {updated} {catechism.abbreviation} questions"
        ))
