import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

# Chapter labels for display
CHAPTER_LABELS = {
    "1": "First Head of Doctrine",
    "2": "Second Head of Doctrine",
    "3&4": "Third and Fourth Heads of Doctrine",
    "4": "Fifth Head of Doctrine",
}


class Command(BaseCommand):
    help = "Load Canons of Dort into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "canons_of_dort.json"
        if data_is_current("catechism-dort", data_path):
            self.stdout.write("Canons of Dort data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        # Count total sections for the catechism record
        total = sum(len(ch["Sections"]) for ch in data["Data"])

        catechism, _ = Catechism.objects.update_or_create(
            slug='dort',
            defaults={
                'name': 'Canons of Dort',
                'abbreviation': 'CD',
                'description': (
                    'The Canons of Dort (1619), issued by the Synod of Dort, '
                    'are a definitive statement of Reformed soteriology in five '
                    'heads of doctrine. They are one of the Three Forms of Unity, '
                    'the confessional standards of the Continental Reformed churches.'
                ),
                'year': 1619,
                'total_questions': total,
                'document_type': Catechism.CONFESSION,
            }
        )

        # Build topics and questions by flattening chapters sequentially
        seq = 0
        for order, chapter in enumerate(data["Data"], start=1):
            ch_key = chapter["Chapter"]
            ch_label = CHAPTER_LABELS.get(ch_key, f"Head {ch_key}")

            section_count = len(chapter["Sections"])
            start = seq + 1
            end = seq + section_count

            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=f"head-{ch_key.replace('&', '-')}",
                defaults={
                    "name": f"{ch_label}: {chapter['Title']}",
                    "order": order,
                    "question_start": start,
                    "question_end": end,
                    "description": chapter["Title"],
                }
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} chapter: {topic.name}")

            for section in chapter["Sections"]:
                seq += 1
                section_id = section["Section"]
                # Parse A1 -> Article 1, R1 -> Rejection of Errors 1
                if section_id.startswith("A"):
                    label = f"{ch_label}, Article {section_id[1:]}"
                elif section_id.startswith("R"):
                    label = f"{ch_label}, Rejection of Errors {section_id[1:]}"
                else:
                    label = f"{ch_label}, Section {section_id}"

                Question.objects.update_or_create(
                    catechism=catechism,
                    number=seq,
                    defaults={
                        "question_text": label,
                        "answer_text": section["Content"],
                        "topic": topic,
                    }
                )

        mark_data_current("catechism-dort", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {seq} Canons of Dort sections"))
