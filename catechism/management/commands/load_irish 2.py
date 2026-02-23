import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

CHAPTERS = [
    {"name": "Of the Holy Scripture and the Three Creeds",
     "slug": "of-holy-scripture-and-creeds",
     "order": 1, "start": 1, "end": 7,
     "description": "The authority of Scripture, the canonical books, and the three ancient creeds"},
    {"name": "Of Faith in the Holy Trinity",
     "slug": "of-the-holy-trinity",
     "order": 2, "start": 8, "end": 10,
     "description": "The one true God in three persons"},
    {"name": "Of God's Eternal Decree and Predestination",
     "slug": "of-gods-eternal-decree",
     "order": 3, "start": 11, "end": 17,
     "description": "God's eternal counsel and the doctrine of predestination"},
    {"name": "Of the Creation, Government, and the Fall",
     "slug": "of-creation-and-the-fall",
     "order": 4, "start": 18, "end": 28,
     "description": "Creation, providence, the fall, and original sin"},
    {"name": "Of Christ and the Application of Redemption",
     "slug": "of-christ-and-redemption",
     "order": 5, "start": 29, "end": 45,
     "description": "Christ the Mediator, justification, sanctification, and good works"},
    {"name": "Of the Service of God and the Civil Magistrate",
     "slug": "of-service-and-magistrate",
     "order": 6, "start": 46, "end": 67,
     "description": "Worship, the civil magistrate, and duties toward neighbours"},
    {"name": "Of the Church and Its Authority",
     "slug": "of-the-church",
     "order": 7, "start": 68, "end": 84,
     "description": "The church, ministry, general councils, and the Old and New Testaments"},
    {"name": "Of the Sacraments",
     "slug": "of-the-sacraments",
     "order": 8, "start": 85, "end": 100,
     "description": "The nature of the sacraments, baptism, and the Lord's Supper"},
    {"name": "Of the State of Souls After Death",
     "slug": "of-the-state-of-souls-after-death",
     "order": 9, "start": 101, "end": 104,
     "description": "The state of souls after death, resurrection, and the last judgment"},
]


class Command(BaseCommand):
    help = "Load Irish Articles of Religion into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "irish_articles.json"
        if data_is_current("catechism-irish", data_path):
            self.stdout.write("Irish Articles data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='irish',
            defaults={
                'name': 'Irish Articles of Religion',
                'abbreviation': 'IAR',
                'description': (
                    'The Irish Articles of Religion (1615), drawn up largely by '
                    'Archbishop James Ussher, were adopted by the Irish Episcopal '
                    'Church. Their 104 articles are widely recognised as a major '
                    'influence on the Westminster Confession of Faith.'
                ),
                'year': 1615,
                'total_questions': 104,
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

        mark_data_current("catechism-irish", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} Irish Articles"
        ))
