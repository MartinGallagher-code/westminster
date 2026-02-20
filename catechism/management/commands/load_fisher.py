import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Question, CommentarySource, Commentary, FisherSubQuestion


class Command(BaseCommand):
    help = "Load Fisher/Erskine commentary from JSON"

    def handle(self, *args, **options):
        source, _ = CommentarySource.objects.update_or_create(
            slug="fisher-erskine",
            defaults={
                "name": "The Assembly's Shorter Catechism Explained",
                "author": "James Fisher & Ebenezer Erskine",
                "year": 1765,
                "description": "A systematic exposition using sub-questions to explore each catechism answer.",
            }
        )

        data_path = settings.BASE_DIR / "data" / "shorter_catechism_explained.json"
        with open(data_path) as f:
            data = json.load(f)

        total_subs = 0
        for entry in data["Data"]:
            num = int(entry["Number"])
            question = Question.objects.get(number=num)

            commentary, _ = Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": ""}
            )

            commentary.sub_questions.all().delete()

            for sq in entry.get("SubQuestions", []):
                FisherSubQuestion.objects.create(
                    commentary=commentary,
                    number=int(sq["Number"]),
                    question_text=sq["Question"],
                    answer_text=sq["Answer"],
                )
                total_subs += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Fisher/Erskine: {len(data['Data'])} entries, {total_subs} sub-questions"
        ))
