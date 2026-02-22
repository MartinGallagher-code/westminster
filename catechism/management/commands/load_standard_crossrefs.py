import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Question, StandardCrossReference


class Command(BaseCommand):
    help = "Load all cross-references into StandardCrossReference table"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "cross_references.json"
        wcf_path = settings.BASE_DIR / "data" / "wcf_cross_references.json"
        paths = [data_path] + ([wcf_path] if wcf_path.exists() else [])
        if data_is_current("standard-crossrefs", *paths):
            self.stdout.write("Standard cross-references unchanged, skipping.")
            return

        catechisms = {c.slug: c for c in Catechism.objects.all()}
        created_count = 0

        # 1. Load WSC <-> WLC from existing file
        with open(data_path) as f:
            data = json.load(f)

        for entry in data:
            wsc_q = Question.objects.filter(
                catechism=catechisms['wsc'], number=entry['wsc']
            ).first()
            if not wsc_q:
                continue
            for wlc_num in entry['wlc']:
                wlc_q = Question.objects.filter(
                    catechism=catechisms['wlc'], number=wlc_num
                ).first()
                if not wlc_q:
                    continue
                _, created = StandardCrossReference.objects.get_or_create(
                    source_question=wsc_q,
                    target_question=wlc_q,
                )
                if created:
                    created_count += 1

        self.stdout.write(f"WSC↔WLC: {created_count} cross-references")

        # 2. Load WCF cross-references
        wcf_path = settings.BASE_DIR / "data" / "wcf_cross_references.json"
        if not wcf_path.exists():
            self.stdout.write(self.style.WARNING("No wcf_cross_references.json found, skipping"))
            return

        wcf_count = 0
        with open(wcf_path) as f:
            wcf_data = json.load(f)

        for entry in wcf_data:
            wcf_q = Question.objects.filter(
                catechism=catechisms['wcf'], number=entry['wcf_section']
            ).first()
            if not wcf_q:
                continue

            for wsc_num in entry.get('wsc', []):
                wsc_q = Question.objects.filter(
                    catechism=catechisms['wsc'], number=wsc_num
                ).first()
                if wsc_q:
                    _, created = StandardCrossReference.objects.get_or_create(
                        source_question=wcf_q, target_question=wsc_q
                    )
                    if created:
                        wcf_count += 1

            for wlc_num in entry.get('wlc', []):
                wlc_q = Question.objects.filter(
                    catechism=catechisms['wlc'], number=wlc_num
                ).first()
                if wlc_q:
                    _, created = StandardCrossReference.objects.get_or_create(
                        source_question=wcf_q, target_question=wlc_q
                    )
                    if created:
                        wcf_count += 1

        self.stdout.write(f"WCF cross-refs: {wcf_count}")
        mark_data_current("standard-crossrefs", *paths)
        self.stdout.write(self.style.SUCCESS(
            f"Total: {created_count + wcf_count} cross-references loaded"
        ))
