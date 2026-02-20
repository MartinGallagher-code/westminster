from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Question, CommentarySource, Commentary


class Command(BaseCommand):
    help = "Load Thomas Vincent commentary from text files"

    def handle(self, *args, **options):
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

        loaded = 0
        for num in range(1, 108):
            filepath = vincent_dir / f"q{num:03d}.txt"
            if not filepath.exists():
                continue

            text = filepath.read_text(encoding="utf-8").strip()
            if not text:
                continue

            question = Question.objects.get(number=num)
            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": text}
            )
            loaded += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded Vincent commentary for {loaded} questions"))
