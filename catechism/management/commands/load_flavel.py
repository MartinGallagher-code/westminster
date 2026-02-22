import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Question, CommentarySource, Commentary, FisherSubQuestion


class Command(BaseCommand):
    help = "Load Flavel commentary from JSON"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "exposition_of_the_assemblies_catechism.json"
        if data_is_current("flavel", data_path):
            self.stdout.write("Flavel data unchanged, skipping.")
            return

        catechism = Catechism.objects.get(slug='wsc')
        source, _ = CommentarySource.objects.update_or_create(
            slug="flavel",
            defaults={
                "name": "An Exposition of the Assemblies Catechism",
                "author": "John Flavel",
                "year": 1688,
                "description": "A thorough exposition with sub-questions covering all 107 questions of the Shorter Catechism.",
            }
        )

        data_path = settings.BASE_DIR / "data" / "exposition_of_the_assemblies_catechism.json"
        with open(data_path) as f:
            data = json.load(f)

        loaded = 0
        total_subs = 0
        for entry in data["Data"]:
            try:
                num = int(entry["Number"])
            except (ValueError, TypeError):
                continue

            question = Question.objects.filter(catechism=catechism, number=num).first()
            if not question:
                continue

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

            loaded += 1

        mark_data_current("flavel", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded Flavel: {loaded} entries, {total_subs} sub-questions"
        ))
