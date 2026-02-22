import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

CHAPTERS = [
    {"name": "God and His Word", "slug": "god-and-his-word",
     "order": 1, "start": 1, "end": 7,
     "description": "The one God and the Holy Scriptures"},
    {"name": "The Holy Trinity", "slug": "the-holy-trinity",
     "order": 2, "start": 8, "end": 11,
     "description": "The Trinity and the deity of the Son and Holy Spirit"},
    {"name": "Creation and Providence", "slug": "creation-and-providence",
     "order": 3, "start": 12, "end": 13,
     "description": "The creation of all things and God's providence"},
    {"name": "Sin and Human Corruption", "slug": "sin-and-human-corruption",
     "order": 4, "start": 14, "end": 15,
     "description": "The fall and original sin"},
    {"name": "Election and Christ's Work", "slug": "election-and-christs-work",
     "order": 5, "start": 16, "end": 21,
     "description": "Election, the incarnation, atonement, and intercession of Christ"},
    {"name": "Justification and the Christian Life", "slug": "justification-and-christian-life",
     "order": 6, "start": 22, "end": 26,
     "description": "Justification by faith, sanctification, and good works"},
    {"name": "The Church", "slug": "the-church",
     "order": 7, "start": 27, "end": 32,
     "description": "The church, its marks, government, and officers"},
    {"name": "The Sacraments", "slug": "the-sacraments",
     "order": 8, "start": 33, "end": 35,
     "description": "The sacraments of Baptism and the Lord's Supper"},
    {"name": "Civil Government and Last Things", "slug": "civil-government-and-last-things",
     "order": 9, "start": 36, "end": 37,
     "description": "The civil magistrate and the last judgment"},
]


class Command(BaseCommand):
    help = "Load Belgic Confession articles into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "belgic_confession_of_faith.json"
        if data_is_current("catechism-belgic", data_path):
            self.stdout.write("Belgic Confession data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='belgic',
            defaults={
                'name': 'Belgic Confession',
                'abbreviation': 'BC',
                'description': (
                    'The Belgic Confession (1561), written by Guido de Bres, is '
                    'a comprehensive statement of Reformed faith in 37 articles. '
                    'It is one of the Three Forms of Unity, the confessional '
                    'standards of the Continental Reformed churches.'
                ),
                'year': 1561,
                'total_questions': 37,
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

        mark_data_current("catechism-belgic", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} Belgic Confession articles"
        ))
