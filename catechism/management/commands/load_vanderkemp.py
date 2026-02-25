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
    help = "Load Vanderkemp commentary on the Heidelberg Catechism from text files"

    def handle(self, *args, **options):
        catechism = Catechism.objects.get(slug='heidelberg')
        source, _ = CommentarySource.objects.update_or_create(
            slug="vanderkemp",
            defaults={
                "name": "The Christian Entirely the Property of Christ",
                "author": "Johannes Vanderkemp",
                "year": 1718,
                "description": (
                    "Fifty-three sermons on the Heidelberg Catechism, "
                    "translated from the Dutch by John M. Van Harlingen "
                    "(New-Brunswick, 1810)."
                ),
            }
        )

        data_dir = settings.BASE_DIR / "data" / "vanderkemp_heidelberg"
        if not data_dir.exists():
            self.stderr.write(self.style.WARNING(
                f"Vanderkemp directory not found: {data_dir}. Skipping."
            ))
            return

        if data_is_current("vanderkemp", data_dir):
            self.stdout.write("Vanderkemp data unchanged, skipping.")
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

        mark_data_current("vanderkemp", data_dir)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded Vanderkemp commentary for {loaded} questions"
        ))
