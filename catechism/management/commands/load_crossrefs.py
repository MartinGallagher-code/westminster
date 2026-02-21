import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.models import Catechism, Question, CrossReference


class Command(BaseCommand):
    help = "Load cross-references between WSC and WLC questions"

    def handle(self, *args, **options):
        try:
            wsc = Catechism.objects.get(slug='wsc')
            wlc = Catechism.objects.get(slug='wlc')
        except Catechism.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                "Both WSC and WLC must be loaded before cross-references."
            ))
            return

        data_path = settings.BASE_DIR / "data" / "cross_references.json"
        with open(data_path) as f:
            data = json.load(f)

        created_count = 0
        for entry in data:
            wsc_num = entry["wsc"]
            wsc_q = Question.objects.filter(catechism=wsc, number=wsc_num).first()
            if not wsc_q:
                self.stderr.write(f"WSC Q{wsc_num} not found, skipping")
                continue

            for wlc_num in entry["wlc"]:
                wlc_q = Question.objects.filter(catechism=wlc, number=wlc_num).first()
                if not wlc_q:
                    self.stderr.write(f"WLC Q{wlc_num} not found, skipping")
                    continue

                _, created = CrossReference.objects.update_or_create(
                    wsc_question=wsc_q,
                    wlc_question=wlc_q,
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {created_count} cross-references"
        ))
