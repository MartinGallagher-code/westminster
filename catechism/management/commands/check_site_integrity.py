"""Assert the loaded site is internally consistent and fetchable.

The unit suite runs against factories: a handful of rows built for one test.
Two real defects survived a green suite because nothing looked at the loaded
database — 25 of 33 doctrine-head chips linked to Atlas pages that did not
exist, and sitemap.xml advertised comparison URLs that returned 404. Both are
invisible to a test that never loads the data.

This command runs after the loaders and checks the things that only a
populated database can answer. It is meant for CI and for a shell on a
deployed instance.
"""

import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import NoReverseMatch, reverse

from catechism.models import Catechism, DoctrineHead, OntologyAttribute, OntologyLocus, Question
from catechism.utils import DEFAULT_TRADITIONS

WESTMINSTER_SLUGS = ('wcf', 'wlc', 'wsc')
EXPECTED_LOCI = 8
EXPECTED_ATTRIBUTES = 35

# Question and section pages are by far the most numerous URLs and the most
# expensive to render; sample them unless --full is given.
DEFAULT_QUESTION_SAMPLE = 25

HREF = re.compile(r'(?:href|action)="(/[^"]*)"')

# Pages whose *rendered links* are checked, one per kind of page. The sitemap
# check answers "does this URL resolve"; this answers "does what the page
# actually links to resolve", which is a different question — the Atlas home
# page linked its text of the day at the upstream mount point, and no sitemap
# check could see it because the sitemap never listed that URL.
LINK_SOURCE_ROUTES = [
    ('catechism:home', {}),
    ('catechism:compare_index', {}),
    ('catechism:scripture_index', {}),
    ('catechism:session_plan', {}),
    ('westminster_standards:home', {}),
    ('westminster_standards:ontology', {}),
    ('westminster_standards:personas_list', {}),
    ('westminster_standards:cruxes_list', {}),
    ('westminster_standards:schools_list', {}),
    ('westminster_standards:heads_list', {}),
    ('westminster_standards:works_list', {}),
    ('westminster_standards:dimension_pairs', {}),
]

# Links a crawl of those pages should not follow: they mutate state, need a
# session, or are static assets served by the storage layer rather than a view.
UNCHECKED_LINK_PREFIXES = ('/static/', '/accounts/', '/admin/')


class Command(BaseCommand):
    help = 'Check the loaded data for broken links and missing relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true',
            help='Fetch every question page rather than a sample.',
        )
        parser.add_argument(
            '--sample', type=int, default=DEFAULT_QUESTION_SAMPLE,
            help='Question pages to fetch per document (default: %(default)s).',
        )

    def handle(self, *args, **options):
        # The test client addresses the app as 'testserver'.
        if 'testserver' not in settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

        self.client = Client()
        self.failures = []

        self._check_documents_loaded()
        self._check_ontology_shape()
        self._check_doctrine_head_coverage()
        self._check_atlas_links_resolve()
        self._check_rendered_links_resolve()
        self._check_sitemap_resolves(
            full=options['full'], sample=options['sample'],
        )

        if self.failures:
            for failure in self.failures:
                self.stderr.write(self.style.ERROR(f'  ✗ {failure}'))
            raise CommandError(
                f'{len(self.failures)} integrity check'
                f'{"" if len(self.failures) == 1 else "s"} failed'
            )
        self.stdout.write(self.style.SUCCESS('All integrity checks passed.'))

    # ── checks ────────────────────────────────────────────────────────────

    def _fail(self, message):
        self.failures.append(message)

    def _ok(self, message):
        self.stdout.write(f'  ✓ {message}')

    def _check_documents_loaded(self):
        missing = [
            slug for slug in WESTMINSTER_SLUGS
            if not Catechism.objects.filter(slug=slug).exists()
        ]
        if missing:
            self._fail(f'Westminster documents not loaded: {", ".join(missing)}')
            return
        self._ok(f'{Catechism.objects.count()} documents loaded')

        unreachable = Catechism.objects.filter(
            tradition=Catechism.OTHER, questions__isnull=False,
        ).exclude(document_type=Catechism.SYSTEMATIC_THEOLOGY).distinct()
        for catechism in unreachable:
            self._fail(
                f'{catechism.abbreviation} has questions but tradition="other", '
                'so every view gates it off'
            )

    def _check_ontology_shape(self):
        loci = OntologyLocus.objects.count()
        attributes = OntologyAttribute.objects.count()
        if loci != EXPECTED_LOCI:
            self._fail(f'expected {EXPECTED_LOCI} ontology loci, found {loci}')
        if attributes != EXPECTED_ATTRIBUTES:
            self._fail(f'expected {EXPECTED_ATTRIBUTES} ontology attributes, found {attributes}')
        if loci == EXPECTED_LOCI and attributes == EXPECTED_ATTRIBUTES:
            self._ok(f'{loci} loci and {attributes} attributes loaded')

        from westminster_standards.heads_of_doctrine import HEADS_OF_DOCTRINE
        atlas_slugs = {head['slug'] for head in HEADS_OF_DOCTRINE}
        db_slugs = set(DoctrineHead.objects.values_list('slug', flat=True))
        if db_slugs != atlas_slugs:
            missing = sorted(atlas_slugs - db_slugs)[:5]
            extra = sorted(db_slugs - atlas_slugs)[:5]
            self._fail(
                'doctrine heads diverge from the Atlas taxonomy '
                f'(missing: {missing}, unexpected: {extra})'
            )
        else:
            self._ok(f'{len(db_slugs)} doctrine heads mirror the Atlas')

    def _check_doctrine_head_coverage(self):
        for slug in WESTMINSTER_SLUGS:
            questions = Question.objects.filter(catechism__slug=slug)
            if not questions.exists():
                continue
            unlinked = questions.filter(doctrine_head_links__isnull=True).count()
            if unlinked:
                self._fail(
                    f'{unlinked} of {questions.count()} {slug.upper()} items '
                    'have no doctrine head'
                )
            else:
                self._ok(f'all {questions.count()} {slug.upper()} items carry a doctrine head')

    def _check_atlas_links_resolve(self):
        broken = [
            head.slug for head in DoctrineHead.objects.all()
            if self.client.get(head.get_atlas_url()).status_code != 200
        ]
        if broken:
            self._fail(f'{len(broken)} doctrine head chips link to a 404: {broken[:5]}')
        elif DoctrineHead.objects.exists():
            self._ok('every doctrine head chip resolves')

        from westminster_standards.sitemap import atlas_sitemap_paths
        paths = atlas_sitemap_paths()
        broken = [path for path in paths if self.client.get(path).status_code != 200]
        if broken:
            self._fail(f'{len(broken)} Atlas pages do not resolve: {broken[:5]}')
        else:
            self._ok(f'all {len(paths)} Atlas pages resolve')

    def _check_rendered_links_resolve(self):
        """Follow every internal link on one page of each kind.

        A crawler and a first-time visitor send no docFilters cookie, so this
        runs as they do: anything a page links to has to resolve under the
        default collections, or the visitor meets a 404 on their first click.
        """
        checked, broken = set(), []
        for route, kwargs in LINK_SOURCE_ROUTES:
            try:
                source = reverse(route, kwargs=kwargs)
            except NoReverseMatch:
                self._fail(f'link-check source route {route} does not exist')
                continue
            page = self.client.get(source)
            if page.status_code != 200:
                self._fail(f'{source} returned {page.status_code}')
                continue
            for href in sorted({h.split('#')[0] for h in HREF.findall(page.content.decode())}):
                if not href or href.startswith(UNCHECKED_LINK_PREFIXES) or href in checked:
                    continue
                checked.add(href)
                status = self.client.get(href).status_code
                if status >= 400:
                    broken.append(f'{href} ({status}) linked from {source}')

        if broken:
            self._fail(
                f'{len(broken)} rendered link(s) do not resolve: {broken[:5]}'
            )
        else:
            self._ok(
                f'{len(checked)} links across {len(LINK_SOURCE_ROUTES)} pages resolve'
            )

    def _check_sitemap_resolves(self, full, sample):
        """Every URL the sitemap advertises must be fetchable by a crawler.

        A crawler sends no docFilters cookie, so this runs exactly as one:
        anonymous, with DEFAULT_TRADITIONS in force.
        """
        from urllib.parse import urlparse
        import re

        response = self.client.get(reverse('catechism:sitemap_xml'))
        if response.status_code != 200:
            self._fail(f'sitemap.xml returned {response.status_code}')
            return

        paths = [
            urlparse(loc).path
            for loc in re.findall(r'<loc>([^<]+)</loc>', response.content.decode())
        ]
        item_paths = [p for p in paths if '/questions/' in p or '/sections/' in p]
        other_paths = [p for p in paths if p not in set(item_paths)]

        checked = list(other_paths)
        if full:
            checked += item_paths
        else:
            # Deterministic spread rather than the first N, so a break late in
            # a document is still caught.
            step = max(1, len(item_paths) // max(1, sample)) if item_paths else 1
            checked += item_paths[::step]

        broken = []
        for path in checked:
            status = self.client.get(path).status_code
            if status != 200:
                broken.append(f'{path} → {status}')
        if broken:
            self._fail(
                f'{len(broken)} of {len(checked)} sitemap URLs do not resolve '
                f'for an anonymous visitor: {broken[:5]}'
            )
        else:
            self._ok(
                f'{len(checked)} of {len(paths)} sitemap URLs checked, all resolve '
                f'(traditions: {", ".join(DEFAULT_TRADITIONS)})'
            )
