import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

CHAPTERS = [
    {"name": "Scripture and God", "slug": "scripture-and-god",
     "order": 1, "start": 1, "end": 5,
     "description": "Holy Scripture, its interpretation, God's nature, and providence"},
    {"name": "Creation, Fall, and Free Will",
     "slug": "creation-fall-and-free-will",
     "order": 2, "start": 6, "end": 9,
     "description": "Creation, the fall, free will, and predestination"},
    {"name": "Christ the Mediator", "slug": "christ-the-mediator",
     "order": 3, "start": 10, "end": 11,
     "description": "Jesus Christ as true God and man, and as Mediator"},
    {"name": "The Law and the Gospel", "slug": "the-law-and-the-gospel",
     "order": 4, "start": 12, "end": 13,
     "description": "The moral law and the gospel of Jesus Christ"},
    {"name": "Salvation and the Christian Life",
     "slug": "salvation-and-christian-life",
     "order": 5, "start": 14, "end": 16,
     "description": "Repentance, justification, faith, and good works"},
    {"name": "The Church", "slug": "the-church",
     "order": 6, "start": 17, "end": 18,
     "description": "The holy catholic church and its ministers"},
    {"name": "Sacraments", "slug": "sacraments",
     "order": 7, "start": 19, "end": 21,
     "description": "The sacraments, baptism, and the Lord's Supper"},
    {"name": "Worship and Assembly", "slug": "worship-and-assembly",
     "order": 8, "start": 22, "end": 25,
     "description": "Sacred assemblies, worship, prayer, and holy days"},
    {"name": "Church Order and Discipline",
     "slug": "church-order-and-discipline",
     "order": 9, "start": 26, "end": 28,
     "description": "Church property, rites, marriage, and burial"},
    {"name": "Civil Government and Last Things",
     "slug": "civil-government-and-last-things",
     "order": 10, "start": 29, "end": 30,
     "description": "The civil magistrate and concluding exhortations"},
]


class Command(BaseCommand):
    help = "Load Second Helvetic Confession chapters into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "second_helvetic_confession.json"
        if data_is_current("catechism-second-helvetic", data_path):
            self.stdout.write("Second Helvetic Confession data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='second-helvetic',
            defaults={
                'name': 'Second Helvetic Confession',
                'abbreviation': 'SHC',
                'description': (
                    'The Second Helvetic Confession (1566), written by Heinrich '
                    'Bullinger, is one of the most widely adopted Reformed '
                    'confessions. Its 30 chapters cover the full range of '
                    'Christian doctrine and were adopted by Reformed churches '
                    'across Switzerland, Scotland, Hungary, Poland, and beyond.'
                ),
                'year': 1566,
                'total_questions': 30,
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

        mark_data_current("catechism-second-helvetic", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} Second Helvetic Confession chapters"
        ))
