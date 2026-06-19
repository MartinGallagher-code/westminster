import json
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question, StandardCrossReference

CHAPTER_RE = re.compile(r"Chapter\s+(\d+)\s*:")


def _expand_ranges(items):
    """Expand a list of ints and [start, end] pairs into a flat set of numbers."""
    numbers = set()
    for item in items:
        if isinstance(item, (list, tuple)):
            start, end = item[0], item[1]
            numbers.update(range(start, end + 1))
        else:
            numbers.add(item)
    return numbers


class Command(BaseCommand):
    help = "Load editorial cross-references from the PCA Book of Church Order to the Westminster Standards"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "pca_bco" / "bco_cross_references.json"
        if not data_path.exists():
            self.stdout.write(self.style.WARNING("No bco_cross_references.json found, skipping"))
            return
        if data_is_current("bco-crossrefs", data_path):
            self.stdout.write("BCO cross-references unchanged, skipping.")
            return

        catechisms = {c.slug: c for c in Catechism.objects.all()}
        bco = catechisms.get("pca-bco")
        wcf = catechisms.get("wcf")
        wlc = catechisms.get("wlc")
        wsc = catechisms.get("wsc")
        if not bco:
            self.stdout.write(self.style.WARNING("PCA BCO not loaded, skipping cross-references"))
            return

        # Map BCO chapter number -> its sequential question-number range, by
        # parsing "Chapter N:" out of the topic name (BCO chapter 44 is vacated,
        # so topic order does not track chapter number reliably).
        bco_chapter_topics = {}
        for topic in Topic.objects.filter(catechism=bco):
            match = CHAPTER_RE.search(topic.name)
            if match:
                bco_chapter_topics[int(match.group(1))] = topic

        # Map WCF chapter number -> question range. WCF topic order tracks the
        # chapter number 1:1 (no preface, no vacated chapters).
        wcf_chapter_topics = {}
        if wcf:
            for topic in Topic.objects.filter(catechism=wcf):
                wcf_chapter_topics[topic.order] = topic

        with open(data_path) as f:
            payload = json.load(f)
        mappings = payload["mappings"] if isinstance(payload, dict) else payload

        created_count = 0
        skipped_chapters = []

        for mapping in mappings:
            chapter = mapping["bco_chapter"]
            bco_topic = bco_chapter_topics.get(chapter)
            if not bco_topic:
                skipped_chapters.append(chapter)
                continue

            bco_questions = list(
                Question.objects.filter(
                    catechism=bco,
                    number__gte=bco_topic.question_start,
                    number__lte=bco_topic.question_end,
                )
            )

            # Collect the target question numbers per catechism.
            target_questions = []

            for wcf_chapter in mapping.get("wcf", []):
                wcf_topic = wcf_chapter_topics.get(wcf_chapter)
                if not wcf_topic:
                    continue
                target_questions.extend(
                    Question.objects.filter(
                        catechism=wcf,
                        number__gte=wcf_topic.question_start,
                        number__lte=wcf_topic.question_end,
                    )
                )

            for target_cat, key in ((wlc, "wlc"), (wsc, "wsc")):
                if not target_cat:
                    continue
                numbers = _expand_ranges(mapping.get(key, []))
                if numbers:
                    target_questions.extend(
                        Question.objects.filter(catechism=target_cat, number__in=numbers)
                    )

            for bco_q in bco_questions:
                for target_q in target_questions:
                    _, created = StandardCrossReference.objects.get_or_create(
                        source_question=bco_q,
                        target_question=target_q,
                    )
                    if created:
                        created_count += 1

        if skipped_chapters:
            self.stdout.write(self.style.WARNING(
                f"Skipped unmapped BCO chapters: {sorted(skipped_chapters)}"
            ))

        mark_data_current("bco-crossrefs", data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {created_count} BCO cross-references"
        ))
