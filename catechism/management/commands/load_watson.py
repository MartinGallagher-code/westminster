import json

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Commentary, CommentarySource, Question


class Command(BaseCommand):
    help = "Load Thomas Watson's Body of Divinity commentary from cached JSON"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "watson_commentary.json"
        if not data_path.exists():
            self.stderr.write(self.style.WARNING(
                f"Watson data file not found: {data_path}. "
                f"Run 'manage.py fetch_watson' first."
            ))
            return

        if data_is_current("watson", data_path):
            self.stdout.write("Watson data unchanged, skipping.")
            return

        catechism = Catechism.objects.get(slug='wsc')

        source, _ = CommentarySource.objects.update_or_create(
            slug="watson",
            defaults={
                "name": "A Body of Divinity",
                "author": "Thomas Watson",
                "year": 1692,
                "description": (
                    "An exposition of the Westminster Shorter Catechism "
                    "(Questions 1-38) delivered as a series of sermons. "
                    "Published posthumously in 1692."
                ),
            },
        )

        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)

        saved = 0
        for qnum_str, body in data.items():
            qnum = int(qnum_str)
            try:
                question = Question.objects.get(catechism=catechism, number=qnum)
            except Question.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(f"  Question {qnum} not found, skipping")
                )
                continue

            Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": body},
            )
            saved += 1

        mark_data_current("watson", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded Watson commentary for {saved} questions"
        ))