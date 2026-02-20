import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Catechism, Topic, Question

WLC_TOPICS = [
    {"name": "Scripture and the Knowledge of God", "slug": "scripture-knowledge-of-god",
     "order": 1, "start": 1, "end": 5,
     "description": "The Scriptures as the Word of God and the rule of faith and life"},
    {"name": "The Nature of God", "slug": "nature-of-god",
     "order": 2, "start": 6, "end": 11,
     "description": "The being, attributes, and persons of the Godhead"},
    {"name": "God's Decrees and Works", "slug": "gods-decrees-and-works",
     "order": 3, "start": 12, "end": 20,
     "description": "God's eternal decrees, creation, and providence"},
    {"name": "The Covenant and the Fall", "slug": "covenant-and-fall",
     "order": 4, "start": 21, "end": 29,
     "description": "The covenant of works, the fall, and the estate of sin and misery"},
    {"name": "Christ the Mediator", "slug": "christ-the-mediator",
     "order": 5, "start": 30, "end": 56,
     "description": "The covenant of grace, the person and offices of Christ the Mediator"},
    {"name": "Effectual Calling and Salvation", "slug": "effectual-calling-salvation",
     "order": 6, "start": 57, "end": 90,
     "description": "The application of redemption: calling, justification, adoption, sanctification, and glory"},
    {"name": "The Moral Law", "slug": "moral-law",
     "order": 7, "start": 91, "end": 97,
     "description": "The moral law, its uses, and the sum of the Ten Commandments"},
    {"name": "The Ten Commandments", "slug": "ten-commandments",
     "order": 8, "start": 98, "end": 148,
     "description": "The duties required and sins forbidden in each commandment"},
    {"name": "The Means of Grace", "slug": "means-of-grace",
     "order": 9, "start": 149, "end": 160,
     "description": "The Word, sacraments, and prayer as means of grace"},
    {"name": "Baptism and the Lord's Supper", "slug": "baptism-lords-supper",
     "order": 10, "start": 161, "end": 177,
     "description": "The nature, administration, and right use of the sacraments"},
    {"name": "Prayer and the Lord's Prayer", "slug": "prayer-lords-prayer",
     "order": 11, "start": 178, "end": 196,
     "description": "The duty of prayer and the petitions of the Lord's Prayer"},
]


class Command(BaseCommand):
    help = "Load WLC questions, answers, and topics into the database"

    def handle(self, *args, **options):
        catechism, _ = Catechism.objects.update_or_create(
            slug='wlc',
            defaults={
                'name': 'Westminster Larger Catechism',
                'abbreviation': 'WLC',
                'description': (
                    'The Westminster Larger Catechism, composed in 1648, contains '
                    '196 questions and answers providing a more comprehensive '
                    'treatment of Christian doctrine than the Shorter Catechism.'
                ),
                'year': 1648,
                'total_questions': 196,
            }
        )

        topic_map = {}
        for t in WLC_TOPICS:
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

        data_path = settings.BASE_DIR / "data" / "westminster_larger_catechism.json"
        with open(data_path) as f:
            data = json.load(f)

        for entry in data["Data"]:
            num = int(entry["Number"])
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

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data['Data'])} WLC questions"))
