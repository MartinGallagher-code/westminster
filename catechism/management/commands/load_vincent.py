import re

from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Question, CommentarySource, Commentary


def clean_text(text):
    """Unwrap paragraphs so text reflows to browser width."""
    paragraphs = re.split(r'\n\s*\n', text)
    unwrapped = []
    for para in paragraphs:
        joined = re.sub(r'\s*\n\s*', ' ', para).strip()
        if joined:
            unwrapped.append(joined)
    return '\n\n'.join(unwrapped)


class Command(BaseCommand):
    help = "Load Thomas Vincent commentary from text files"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='wsc')
        source, _ = CommentarySource.objects.update_or_create(
            slug="vincent",
            defaults={
                "name": "The Shorter Catechism Explained from Scripture",
                "author": "Thomas Vincent",
                "year": 1674,
                "description": "A clear and practical exposition with abundant Scripture proofs.",
            }
        )

        vincent_dir = settings.BASE_DIR / "data" / "vincent_commentary"
        if not vincent_dir.exists():
            self.stderr.write(self.style.WARNING(
                f"Vincent directory not found: {vincent_dir}. Skipping."
            ))
            return

        if data_is_current("vincent", vincent_dir):
            self.stdout.write("Vincent data unchanged, skipping.")
            return

        loaded = 0
        for num in range(1, 108):
            filepath = vincent_dir / f"q{num:03d}.txt"
            if not filepath.exists():
                continue

            text = clean_text(filepath.read_text(encoding="utf-8")).strip()
            if not text:
                continue

            question = Question.objects.get(catechism=catechism, number=num)
            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": text}
            )
            loaded += 1

        mark_data_current("vincent", vincent_dir)
        self.stdout.write(self.style.SUCCESS(f"Loaded Vincent commentary for {loaded} questions"))
