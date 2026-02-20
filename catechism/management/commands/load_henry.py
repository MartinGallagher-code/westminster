import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Question, CommentarySource, Commentary, FisherSubQuestion


class Command(BaseCommand):
    help = "Load Matthew Henry commentary from JSON"

    def handle(self, *args, **options):
        source, _ = CommentarySource.objects.update_or_create(
            slug="henry",
            defaults={
                "name": "A Scripture Catechism",
                "author": "Matthew Henry",
                "year": 1703,
                "description": "Scripture-based exposition with sub-questions illuminating each answer from the Word of God.",
            }
        )

        data_path = settings.BASE_DIR / "data" / "matthew_henrys_scripture_catechism.json"
        with open(data_path) as f:
            data = json.load(f)

        loaded = 0
        total_subs = 0
        for entry in data["Data"]:
            try:
                num = int(entry["Number"])
            except (ValueError, TypeError):
                continue

            question = Question.objects.filter(number=num).first()
            if not question:
                continue

            commentary, _ = Commentary.objects.update_or_create(
                question=question,
                source=source,
                defaults={"body": ""}
            )

            commentary.sub_questions.all().delete()

            for idx, sq in enumerate(entry.get("SubQuestions", []), start=1):
                FisherSubQuestion.objects.create(
                    commentary=commentary,
                    number=idx,
                    question_text=sq["Question"],
                    answer_text=sq["Answer"],
                )
                total_subs += 1

            loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded Henry: {loaded} entries, {total_subs} sub-questions"
        ))
