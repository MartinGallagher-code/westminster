import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

TOPICS = [
    {"name": "Man's Misery", "slug": "mans-misery", "order": 1,
     "start": 1, "end": 11,
     "description": "The knowledge of our sin and misery"},
    {"name": "God the Father", "slug": "god-the-father", "order": 2,
     "start": 12, "end": 28,
     "description": "God the Father and creation, as confessed in the Apostles' Creed"},
    {"name": "God the Son", "slug": "god-the-son", "order": 3,
     "start": 29, "end": 52,
     "description": "The Lord Jesus Christ: His person, offices, and states"},
    {"name": "God the Holy Spirit", "slug": "god-the-holy-spirit", "order": 4,
     "start": 53, "end": 58,
     "description": "The Holy Spirit, the church, forgiveness, resurrection, and eternal life"},
    {"name": "The Sacraments", "slug": "the-sacraments", "order": 5,
     "start": 59, "end": 82,
     "description": "The sacraments of Baptism and the Lord's Supper"},
    {"name": "Church Discipline", "slug": "church-discipline", "order": 6,
     "start": 83, "end": 85,
     "description": "The office of the keys and church discipline"},
    {"name": "The Ten Commandments", "slug": "the-ten-commandments", "order": 7,
     "start": 86, "end": 115,
     "description": "Gratitude expressed through obedience to the Ten Commandments"},
    {"name": "Prayer and the Lord's Prayer", "slug": "prayer-and-lords-prayer", "order": 8,
     "start": 116, "end": 129,
     "description": "Prayer as the chief part of thankfulness, and the Lord's Prayer"},
]


class Command(BaseCommand):
    help = "Load Heidelberg Catechism questions and answers into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "heidelberg_catechism.json"
        if data_is_current("catechism-heidelberg", data_path):
            self.stdout.write("Heidelberg Catechism data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='heidelberg',
            defaults={
                'name': 'Heidelberg Catechism',
                'abbreviation': 'HC',
                'description': (
                    'The Heidelberg Catechism (1563) is a Reformed catechism of '
                    '129 questions and answers organized around the themes of '
                    'guilt, grace, and gratitude. It is one of the Three Forms '
                    'of Unity, the confessional standards of the Continental '
                    'Reformed churches.'
                ),
                'year': 1563,
                'total_questions': 129,
            }
        )

        topic_map = {}
        for t in TOPICS:
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
            self.stdout.write(f"{'Created' if created else 'Updated'} topic: {topic.name}")

        with open(data_path) as f:
            data = json.load(f)

        for entry in data["Data"]:
            num = entry["Number"]
            topic = None
            for (start, end), t in topic_map.items():
                if start <= num <= end:
                    topic = t
                    break

            Question.objects.update_or_create(
                catechism=catechism,
                number=num,
                defaults={
                    "question_text": entry["Question"],
                    "answer_text": entry["Answer"],
                    "topic": topic,
                }
            )

        mark_data_current("catechism-heidelberg", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data['Data'])} Heidelberg Catechism questions"))
