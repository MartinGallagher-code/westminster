import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

INSTITUTES_BOOKS = [
    {
        "name": "Book I: Knowledge of God the Creator",
        "slug": "book-1-knowledge-of-god-the-creator",
        "order": 1,
        "start": 1,
        "end": 18,
        "description": (
            "The knowledge of God as Creator, including natural revelation, "
            "the corruption of human knowledge by idolatry, and Scripture as "
            "the true spectacles through which God is known."
        ),
    },
    {
        "name": "Book II: Knowledge of God the Redeemer",
        "slug": "book-2-knowledge-of-god-the-redeemer",
        "order": 2,
        "start": 19,
        "end": 35,
        "description": (
            "The fall of man, the law, the mediatorial work of Christ, "
            "and His threefold office as Prophet, Priest, and King."
        ),
    },
    {
        "name": "Book III: The Mode of Obtaining the Grace of Christ",
        "slug": "book-3-mode-of-obtaining-grace",
        "order": 3,
        "start": 36,
        "end": 60,
        "description": (
            "Faith, regeneration, justification by faith alone, Christian liberty, "
            "prayer, election and predestination, and the resurrection."
        ),
    },
    {
        "name": "Book IV: The External Means of Grace",
        "slug": "book-4-external-means-of-grace",
        "order": 4,
        "start": 61,
        "end": 80,
        "description": (
            "The church, its government and ministry, the sacraments of baptism "
            "and the Lord's Supper, and the relation of the church to civil government."
        ),
    },
]


class Command(BaseCommand):
    help = "Load Calvin's Institutes of the Christian Religion (Beveridge, 1845)"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "calvins_institutes.json"
        if not data_path.exists():
            self.stdout.write(self.style.WARNING(
                "calvins_institutes.json not found. "
                "Run scripts/parse_calvins_institutes.py first."
            ))
            return

        if data_is_current("calvins-institutes", data_path):
            self.stdout.write("Institutes data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        catechism, _ = Catechism.objects.update_or_create(
            slug='institutes',
            defaults={
                'name': "Institutes of the Christian Religion",
                'abbreviation': 'Inst',
                'description': (
                    "Calvin's Institutes of the Christian Religion (1559), "
                    "translated by Henry Beveridge (1845). The foundational "
                    "systematic exposition of Reformed theology, organized in "
                    "four books covering the knowledge of God the Creator, God "
                    "the Redeemer, the manner of obtaining grace, and the "
                    "external means of grace."
                ),
                'year': 1559,
                'total_questions': len(data["Data"]),
                'document_type': Catechism.SYSTEMATIC_THEOLOGY,
            }
        )

        topic_map = {}
        for b in INSTITUTES_BOOKS:
            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=b["slug"],
                defaults={
                    "name": b["name"],
                    "order": b["order"],
                    "question_start": b["start"],
                    "question_end": b["end"],
                    "description": b["description"],
                }
            )
            topic_map[(b["start"], b["end"])] = topic
            self.stdout.write(f"{'Created' if created else 'Updated'} book: {topic.name}")

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
                    "question_text": entry["ChapterTitle"],
                    "answer_text": entry["Text"],
                    "topic": topic,
                    "proof_texts": entry.get("ProofTexts", ""),
                }
            )

        mark_data_current("calvins-institutes", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} chapters of the Institutes"
        ))
