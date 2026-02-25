import re

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Commentary, CommentarySource, Question


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
    help = "Load Fisher's Exercises on the Heidelberg Catechism from text files"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='heidelberg')
        source, _ = CommentarySource.objects.update_or_create(
            slug="fisher-hc",
            defaults={
                "name": "Exercises on the Heidelberg Catechism",
                "author": "Samuel R. Fisher",
                "year": 1854,
                "description": (
                    "Catechetical exercises on the Heidelberg Catechism, "
                    "with explanations, doctrines, and proofs "
                    "(Publication Office of the German Reformed Church, 1854)."
                ),
            }
        )

        data_dir = settings.BASE_DIR / "data" / "fisher_heidelberg"
        if not data_dir.exists():
            self.stderr.write(self.style.WARNING(
                f"Fisher HC directory not found: {data_dir}. Skipping."
            ))
            return

        if data_is_current("fisher-hc", data_dir):
            self.stdout.write("Fisher HC data unchanged, skipping.")
            return

        loaded = 0
        for num in range(1, 130):
            filepath = data_dir / f"q{num:03d}.txt"
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

        mark_data_current("fisher-hc", data_dir)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded Fisher HC commentary for {loaded} questions"
        ))
