import json
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question


class Command(BaseCommand):
    help = "Load PCA Book of Church Order chapters and sections into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "pca_bco" / "pca_bco.json"
        if data_is_current("catechism-pca-bco", data_path):
            self.stdout.write("PCA BCO data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        # Count total sections (preface + all chapters)
        total = len(data['preface'])
        for part in data['parts']:
            for ch in part['chapters']:
                total += len(ch['sections'])

        catechism, _ = Catechism.objects.update_or_create(
            slug='pca-bco',
            defaults={
                'name': 'Book of Church Order (PCA)',
                'abbreviation': 'BCO',
                'description': (
                    'The Book of Church Order of the Presbyterian Church in America, '
                    'comprising the Form of Government, the Rules of Discipline, and '
                    'the Directory for the Worship of God. 2024 edition, including '
                    'amendments through the 51st General Assembly.'
                ),
                'year': 2024,
                'total_questions': total,
                'document_type': Catechism.CONFESSION,
                'tradition': Catechism.WESTMINSTER,
            }
        )

        # Clear existing data for a clean reload
        Question.objects.filter(catechism=catechism).delete()
        Topic.objects.filter(catechism=catechism).delete()

        seq = 1  # sequential question number
        topic_order = 0

        # Preface topic
        topic_order += 1
        preface_start = seq
        preface_end = seq + len(data['preface']) - 1
        topic, created = Topic.objects.update_or_create(
            catechism=catechism,
            slug='preface',
            defaults={
                'name': 'Preface',
                'order': topic_order,
                'question_start': preface_start,
                'question_end': preface_end,
                'description': 'The King and Head of the Church, Preliminary Principles, and the Constitution Defined',
            }
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} topic: {topic.name}")

        # Load preface sections as Questions
        for ps in data['preface']:
            Question.objects.update_or_create(
                catechism=catechism,
                number=seq,
                defaults={
                    'question_text': ps['title'],
                    'answer_text': ps['text'],
                    'topic': topic,
                    'proof_texts': '',
                }
            )
            seq += 1

        # Load each chapter
        for part in data['parts']:
            for ch in part['chapters']:
                if not ch['sections']:
                    continue

                topic_order += 1
                ch_start = seq
                ch_end = seq + len(ch['sections']) - 1

                topic, created = Topic.objects.update_or_create(
                    catechism=catechism,
                    slug=slugify(f"ch-{ch['chapter']}-{ch['title']}")[:50].rstrip('-'),
                    defaults={
                        'name': f"Chapter {ch['chapter']}: {ch['title']}",
                        'order': topic_order,
                        'question_start': ch_start,
                        'question_end': ch_end,
                        'description': f"{part['part']} — {part['title']}",
                    }
                )
                self.stdout.write(f"{'Created' if created else 'Updated'} topic: {topic.name}")

                for section in ch['sections']:
                    Question.objects.update_or_create(
                        catechism=catechism,
                        number=seq,
                        defaults={
                            'question_text': section['number'],
                            'answer_text': section['text'],
                            'topic': topic,
                            'proof_texts': '',
                        }
                    )
                    seq += 1

        mark_data_current("catechism-pca-bco", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {seq - 1} PCA BCO sections"))
