import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

TOPICS = [
    {"name": "God as Creator", "slug": "god-as-creator", "order": 1,
     "start": 1, "end": 12,
     "description": "The nature and works of God as Creator and Sustainer"},
    {"name": "Sin and Human Nature", "slug": "sin-and-human-nature", "order": 2,
     "start": 13, "end": 20,
     "description": "The fall, sin, and the misery of humanity"},
    {"name": "Christ the Redeemer", "slug": "christ-the-redeemer", "order": 3,
     "start": 21, "end": 38,
     "description": "The person and work of Christ, and the application of redemption"},
    {"name": "The Ten Commandments", "slug": "the-ten-commandments", "order": 4,
     "start": 39, "end": 84,
     "description": "The moral law and what God requires of man"},
    {"name": "The Sacraments", "slug": "the-sacraments", "order": 5,
     "start": 85, "end": 97,
     "description": "Baptism and the Lord's Supper as means of grace"},
    {"name": "The Lord's Prayer", "slug": "the-lords-prayer", "order": 6,
     "start": 98, "end": 107,
     "description": "Prayer and the petitions of the Lord's Prayer"},
]


class Command(BaseCommand):
    help = "Load WSC questions, answers, and topics into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "westminster_shorter_catechism.json"
        if data_is_current("catechism-wsc", data_path):
            self.stdout.write("WSC data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='wsc',
            defaults={
                'name': 'Westminster Shorter Catechism',
                'abbreviation': 'WSC',
                'description': (
                    'The Westminster Shorter Catechism, composed in 1647, contains 107 questions'
                    ' and answers summarizing the essential doctrines of the Christian faith.'
                ),
                'year': 1647,
                'total_questions': 107,
                'tradition': Catechism.WESTMINSTER,
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

        data_path = settings.BASE_DIR / "data" / "westminster_shorter_catechism.json"
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

        mark_data_current("catechism-wsc", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data['Data'])} questions"))
