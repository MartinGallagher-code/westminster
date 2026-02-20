import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Question


class Command(BaseCommand):
    help = "Load proof text references into Question records"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "proof_texts.json"
        if not data_path.exists():
            self.stderr.write(self.style.WARNING(
                f"Proof texts file not found: {data_path}. Skipping."
            ))
            return

        with open(data_path) as f:
            proof_data = json.load(f)

        updated = 0
        for num_str, refs in proof_data.items():
            count = Question.objects.filter(number=int(num_str)).update(proof_texts=refs)
            updated += count

        self.stdout.write(self.style.SUCCESS(f"Updated proof texts for {updated} questions"))
