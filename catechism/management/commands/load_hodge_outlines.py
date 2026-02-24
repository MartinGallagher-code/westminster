import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

OUTLINES_PARTS = [
    {
        "name": "Part I: Prolegomena",
        "slug": "part-1-prolegomena",
        "order": 1,
        "start": 1,
        "end": 7,
        "description": (
            "The nature and branches of Christian theology, proof of God's existence, "
            "the sources and inspiration of Scripture, and the role of creeds and confessions."
        ),
    },
    {
        "name": "Part II: Theology Proper",
        "slug": "part-2-theology-proper",
        "order": 2,
        "start": 8,
        "end": 11,
        "description": "The attributes of God, the Holy Trinity, and the divine decrees including predestination.",
    },
    {
        "name": "Part III: Creation and Providence",
        "slug": "part-3-creation-and-providence",
        "order": 3,
        "start": 12,
        "end": 14,
        "description": "The creation of the world, angels, and the doctrine of divine providence.",
    },
    {
        "name": "Part IV: Anthropology and Hamartiology",
        "slug": "part-4-anthropology-and-hamartiology",
        "order": 4,
        "start": 15,
        "end": 21,
        "description": (
            "The moral constitution of man, his original state, the covenant of works, "
            "the nature of sin, original sin, inability, and the imputation of Adam's sin."
        ),
    },
    {
        "name": "Part V: Christology",
        "slug": "part-5-christology",
        "order": 5,
        "start": 22,
        "end": 27,
        "description": (
            "The covenant of grace, the person of Christ, His mediatorial office, "
            "the atonement, His intercession, and His mediatorial kingship."
        ),
    },
    {
        "name": "Part VI: Soteriology",
        "slug": "part-6-soteriology",
        "order": 6,
        "start": 28,
        "end": 36,
        "description": (
            "Effectual calling, regeneration, faith, union with Christ, repentance, "
            "justification, adoption, sanctification, and perseverance of the saints."
        ),
    },
    {
        "name": "Part VII: Eschatology",
        "slug": "part-7-eschatology",
        "order": 7,
        "start": 37,
        "end": 40,
        "description": "Death and the state of the soul, the resurrection, the second advent and judgment, and heaven and hell.",
    },
    {
        "name": "Part VIII: Ecclesiology and the Sacraments",
        "slug": "part-8-ecclesiology-and-sacraments",
        "order": 8,
        "start": 41,
        "end": 43,
        "description": "The nature of the sacraments, baptism, and the Lord's Supper.",
    },
]


class Command(BaseCommand):
    help = "Load A.A. Hodge's Outlines of Theology (1879)"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "hodge_outlines.json"
        if not data_path.exists():
            self.stdout.write(self.style.WARNING(
                "hodge_outlines.json not found. "
                "Run scripts/parse_hodge_outlines.py first."
            ))
            return

        if data_is_current("hodge-outlines", data_path):
            self.stdout.write("Hodge Outlines data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        catechism, _ = Catechism.objects.update_or_create(
            slug='hodge-outlines',
            defaults={
                'name': "Outlines of Theology",
                'abbreviation': 'HOT',
                'description': (
                    "A.A. Hodge's Outlines of Theology (1860, revised 1879). "
                    "A concise systematic theology in the Princeton Reformed "
                    "tradition, covering the full range of Christian doctrine "
                    "from prolegomena to eschatology."
                ),
                'year': 1860,
                'total_questions': len(data["Data"]),
                'document_type': Catechism.SYSTEMATIC_THEOLOGY,
            }
        )

        topic_map = {}
        for p in OUTLINES_PARTS:
            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=p["slug"],
                defaults={
                    "name": p["name"],
                    "order": p["order"],
                    "question_start": p["start"],
                    "question_end": p["end"],
                    "description": p["description"],
                }
            )
            topic_map[(p["start"], p["end"])] = topic
            self.stdout.write(f"{'Created' if created else 'Updated'} part: {topic.name}")

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

        mark_data_current("hodge-outlines", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(data['Data'])} chapters of Hodge's Outlines"
        ))
