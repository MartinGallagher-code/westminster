import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Topic, Question

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
        topic_map = {}
        for t in TOPICS:
            topic, created = Topic.objects.update_or_create(
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
                number=num,
                defaults={
                    "question_text": entry["Question"],
                    "answer_text": entry["Answer"],
                    "topic": topic,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data['Data'])} questions"))
