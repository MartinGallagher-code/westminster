from itertools import combinations

from django.core.management.base import BaseCommand
from django.conf import settings

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import (
    Question, StandardCrossReference,
    ComparisonSet, ComparisonTheme,
)

# Cross-set mapping: Westminster theme slug -> list of TFU theme slugs.
# Derived by aligning theological locus/topic across the two traditions.
WESTMINSTER_TO_TFU = {
    'mans-chief-end-and-holy-scripture': [
        'mans-comfort-and-knowledge-of-god',
        'holy-scripture',
    ],
    'god-and-the-holy-trinity': ['god-and-the-holy-trinity'],
    'gods-eternal-decree': ['election-and-predestination'],
    'creation': ['creation-and-providence'],
    'providence': ['creation-and-providence'],
    'fall-sin-and-misery': ['fall-and-original-sin'],
    'covenant-of-grace': ['christ-the-redeemer'],
    'christ-the-mediator': ['christ-the-redeemer', 'the-atonement'],
    'effectual-calling': ['regeneration-and-conversion'],
    'justification': ['justification-by-faith'],
    'sanctification': ['sanctification-and-good-works'],
    'saving-faith-repentance-and-good-works': ['sanctification-and-good-works'],
    'perseverance-and-assurance': ['perseverance-of-the-saints'],
    'the-moral-law': ['the-ten-commandments'],
    'the-ten-commandments-expounded': ['the-ten-commandments'],
    'the-church': ['the-church', 'church-discipline'],
    'sacraments-and-means-of-grace': ['sacraments-baptism-and-lords-supper'],
    'church-government-and-discipline': ['church-discipline'],
    'prayer': ['prayer-and-lords-prayer'],
    'death-resurrection-and-last-judgment': ['civil-magistrate-and-last-judgment'],
    'oaths-magistrate-and-marriage': ['civil-magistrate-and-last-judgment'],
}

MAX_TARGET_RANGE = 5


class Command(BaseCommand):
    help = "Generate cross-references between all documents from comparison theme data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be created without writing to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Data versioning: skip if comparison theme files haven't changed
        data_dir = settings.BASE_DIR / "data"
        theme_files = [
            data_dir / "comparison_themes.json",
            data_dir / "comparison_themes_tfu.json",
            data_dir / "comparison_themes_1689.json",
            data_dir / "comparison_themes_pre_westminster.json",
        ]
        existing_files = [f for f in theme_files if f.exists()]
        if not dry_run and data_is_current("theme-crossrefs", *existing_files):
            self.stdout.write("Theme cross-reference data unchanged, skipping.")
            return

        # Pre-cache all questions keyed by (catechism_slug, number)
        self.question_cache = {}
        for q in Question.objects.select_related('catechism', 'topic').all():
            self.question_cache[(q.catechism.slug, q.number)] = q

        # Pre-load existing cross-reference pairs for deduplication
        self.existing_pairs = set()
        for src_id, tgt_id in StandardCrossReference.objects.values_list(
            'source_question_id', 'target_question_id'
        ):
            self.existing_pairs.add(frozenset((src_id, tgt_id)))

        self.to_create = []

        # Phase 1: Intra-set cross-references
        phase1 = self._phase1_intra_set()
        self.stdout.write(f"  Phase 1 (intra-set): {phase1}")

        # Phase 2: Cross-set (Westminster <-> TFU)
        phase2 = self._phase2_cross_set()
        self.stdout.write(f"  Phase 2 (cross-set): {phase2}")

        # Phase 3: Transitive (1689 <-> WSC/WLC and 1689 <-> TFU)
        phase3 = self._phase3_transitive()
        self.stdout.write(f"  Phase 3 (transitive): {phase3}")

        total = phase1 + phase2 + phase3

        if not dry_run and self.to_create:
            StandardCrossReference.objects.bulk_create(
                self.to_create, batch_size=500, ignore_conflicts=True,
            )
            mark_data_current("theme-crossrefs", *existing_files)

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}Total: {total} theme-based cross-references created"
        ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_crossref(self, src_q, tgt_q):
        """Queue a cross-reference for creation. Returns 1 if new, 0 if exists."""
        if src_q is None or tgt_q is None:
            return 0
        if src_q.catechism_id == tgt_q.catechism_id:
            return 0
        pair = frozenset((src_q.id, tgt_q.id))
        if pair in self.existing_pairs:
            return 0
        self.existing_pairs.add(pair)
        self.to_create.append(StandardCrossReference(
            source_question=src_q, target_question=tgt_q,
        ))
        return 1

    def _crossrefs_for_ranges(self, src_slug, src_start, src_end,
                              tgt_slug, tgt_start, tgt_end):
        """Create cross-references between two question ranges.

        Every source question gets a link to the target document.
        If the target range is small (≤ MAX_TARGET_RANGE), each source
        links to ALL target questions.  Otherwise, each source links
        only to the FIRST target question.  Display truncation in the
        template handles any resulting clutter on the target side.
        """
        if src_slug == tgt_slug:
            return 0
        target_size = tgt_end - tgt_start + 1
        created = 0
        for src_num in range(src_start, src_end + 1):
            src_q = self.question_cache.get((src_slug, src_num))
            if not src_q:
                continue
            if target_size <= MAX_TARGET_RANGE:
                for tgt_num in range(tgt_start, tgt_end + 1):
                    tgt_q = self.question_cache.get((tgt_slug, tgt_num))
                    created += self._add_crossref(src_q, tgt_q)
            else:
                tgt_q = self.question_cache.get((tgt_slug, tgt_start))
                created += self._add_crossref(src_q, tgt_q)
        return created

    def _get_theme_entries(self, theme):
        """Return list of (catechism_slug, start, end) tuples for a theme."""
        return [
            (e.catechism.slug, e.question_start, e.question_end)
            for e in theme.entries.select_related('catechism').all()
        ]

    # ------------------------------------------------------------------
    # Phase 1: Intra-set cross-references
    # ------------------------------------------------------------------

    def _phase1_intra_set(self):
        count = 0
        for cs in ComparisonSet.objects.all():
            for theme in cs.themes.all():
                entries = self._get_theme_entries(theme)
                for (s1, start1, end1), (s2, start2, end2) in combinations(entries, 2):
                    count += self._crossrefs_for_ranges(
                        s1, start1, end1, s2, start2, end2,
                    )
        return count

    # ------------------------------------------------------------------
    # Phase 2: Cross-set (Westminster <-> TFU)
    # ------------------------------------------------------------------

    def _phase2_cross_set(self):
        count = 0
        try:
            west_set = ComparisonSet.objects.get(slug='westminster')
            tfu_set = ComparisonSet.objects.get(slug='three-forms')
        except ComparisonSet.DoesNotExist:
            return 0

        west_themes = {
            t.slug: t for t in west_set.themes.all()
        }
        tfu_themes = {
            t.slug: t for t in tfu_set.themes.all()
        }

        for west_slug, tfu_slugs in WESTMINSTER_TO_TFU.items():
            west_theme = west_themes.get(west_slug)
            if not west_theme:
                continue
            west_entries = self._get_theme_entries(west_theme)

            for tfu_slug in tfu_slugs:
                tfu_theme = tfu_themes.get(tfu_slug)
                if not tfu_theme:
                    continue
                tfu_entries = self._get_theme_entries(tfu_theme)

                for w_slug, w_start, w_end in west_entries:
                    if w_slug not in ('wsc', 'wlc', 'wcf'):
                        continue
                    for t_slug, t_start, t_end in tfu_entries:
                        if t_slug not in ('heidelberg', 'belgic', 'dort'):
                            continue
                        count += self._crossrefs_for_ranges(
                            w_slug, w_start, w_end,
                            t_slug, t_start, t_end,
                        )
        return count

    # ------------------------------------------------------------------
    # Phase 3: Transitive (1689 <-> WSC/WLC and 1689 <-> TFU)
    # ------------------------------------------------------------------

    def _phase3_transitive(self):
        count = 0
        try:
            baptist_set = ComparisonSet.objects.get(slug='1689-baptist')
            west_set = ComparisonSet.objects.get(slug='westminster')
            tfu_set = ComparisonSet.objects.get(slug='three-forms')
        except ComparisonSet.DoesNotExist:
            return 0

        tfu_themes_map = {
            t.slug: t for t in tfu_set.themes.all()
        }

        for theme in baptist_set.themes.all():
            entries_by_slug = {}
            for e in theme.entries.select_related('catechism').all():
                entries_by_slug[e.catechism.slug] = (
                    e.question_start, e.question_end
                )

            wcf_range = entries_by_slug.get('wcf')
            e1689_range = entries_by_slug.get('1689')
            if not wcf_range or not e1689_range:
                continue

            # 3a: 1689 <-> WSC/WLC via overlapping Westminster themes
            overlapping = ComparisonTheme.objects.filter(
                comparison_set=west_set,
                entries__catechism__slug='wcf',
                entries__question_start__lte=wcf_range[1],
                entries__question_end__gte=wcf_range[0],
            ).distinct()

            for wt in overlapping:
                for w_slug, w_start, w_end in self._get_theme_entries(wt):
                    if w_slug in ('wsc', 'wlc'):
                        count += self._crossrefs_for_ranges(
                            '1689', e1689_range[0], e1689_range[1],
                            w_slug, w_start, w_end,
                        )

                # 3b: 1689 <-> TFU via Westminster -> TFU mapping
                tfu_slugs = WESTMINSTER_TO_TFU.get(wt.slug, [])
                for tfu_slug in tfu_slugs:
                    tfu_theme = tfu_themes_map.get(tfu_slug)
                    if not tfu_theme:
                        continue
                    for t_slug, t_start, t_end in self._get_theme_entries(tfu_theme):
                        if t_slug in ('heidelberg', 'belgic', 'dort'):
                            count += self._crossrefs_for_ranges(
                                '1689', e1689_range[0], e1689_range[1],
                                t_slug, t_start, t_end,
                            )

        return count
