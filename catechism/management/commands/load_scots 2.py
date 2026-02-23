import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

CHAPTERS = [
    {"name": "God and the Trinity", "slug": "god-and-the-trinity",
     "order": 1, "start": 1, "end": 1,
     "description": "The one God in three persons"},
    {"name": "Creation and the Fall", "slug": "creation-and-the-fall",
     "order": 2, "start": 2, "end": 3,
     "description": "The creation of man and original sin"},
    {"name": "The Promise and the Law", "slug": "the-promise-and-the-law",
     "order": 3, "start": 4, "end": 5,
     "description": "The promise of redemption and the continuity of the Kirk"},
    {"name": "The Incarnation and Passion", "slug": "incarnation-and-passion",
     "order": 4, "start": 6, "end": 11,
     "description": "The incarnation, passion, resurrection, and ascension of Christ"},
    {"name": "Salvation and the Holy Spirit", "slug": "salvation-and-holy-spirit",
     "order": 5, "start": 12, "end": 15,
     "description": "Faith, good works, and the work of the Holy Spirit"},
    {"name": "The Kirk", "slug": "the-kirk",
     "order": 6, "start": 16, "end": 20,
     "description": "The nature, authority, and marks of the true Kirk"},
    {"name": "Sacraments", "slug": "sacraments",
     "order": 7, "start": 21, "end": 23,
     "description": "The sacraments of Baptism and the Lord's Supper"},
    {"name": "Civil Government and Last Things",
     "slug": "civil-government-and-last-things",
     "order": 8, "start": 24, "end": 25,
     "description": "The civil magistrate and the final resurrection"},
]


class Command(BaseCommand):
    help = "Load Scots Confession articles into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "scots_confession.json"
        if data_is_current("catechism-scots", data_path):
            self.stdout.write("Scots Confession data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='scots',
            defaults={
                'name': 'Scots Confession',
                'abbreviation': 'SC60',
                'description': (
                    'The Scots Confession (1560), drafted by John Knox and five '
                    'other reformers, was the first confession of faith of the '
                    'Reformed Church of Scotland. Its 25 articles remained the '
                    'subordinate standard of the Church of Scotland until '
                    'superseded by the Westminster Confession in 1647.'
                ),
                'year': 1560,
                'total_questions': 25,
                'document_type': Catechism.CONFESSION,
            }
        )

        topic_map = {}
        for t in CHAPTERS:
            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=t["slug"],
                defaults={
                    "name": t["name"],
                    "order": t["order"],
                    "question_start": t["start"],
                    "question_end": t["end"],
                    "description": t["description"],
                }
            )
            topic_map[(t["start"], t["end"])] = topic
            self.stdout.write(f"{'Created' if created else 'Updated'} chapter: {topic.name}")

        with open(data_path) as f:
            data = json.load(f)

        for entry in data["Data"]:
            num = int(entry["Article"])
            topic = None
            for (start, end), t in topic_map.items():
                if start <= num <= end:
                    topic = t
                    break

            Question.objects.update_or_create(
                catechism=catechism,
                number=num,
                defaults={
                    "question_text": entry["Title"],
                    "answer_text": entry["Content"],
                    "topic": topic,
                }
            )

        mark_data_current("catechism-scots", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} Scots Confession articles"
        ))
