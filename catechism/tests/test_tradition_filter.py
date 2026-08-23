"""
Tests for the site-wide tradition filter:
  - get_active_traditions() utility (Phase 1)
  - Filtered view querysets (Phases 2-6)
"""
import json
import re
from urllib.parse import urlparse

import pytest
from django.test import Client, RequestFactory

from catechism.models import Catechism, ComparisonSet
from catechism.utils import get_active_traditions
from .conftest import (
    CatechismFactory, ComparisonSetFactory, TopicFactory, QuestionFactory,
    BibleBookFactory, ScriptureIndexFactory,
    ComparisonThemeFactory, ComparisonEntryFactory,
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def client_with_cookie(filters: dict) -> Client:
    """Return a Django test Client with a pre-set docFilters cookie."""
    c = Client()
    c.cookies['docFilters'] = json.dumps(filters)
    return c


# ─── 8.1  get_active_traditions() unit tests ────────────────────────────────

@pytest.mark.django_db
class TestGetActiveTraditions:
    """Unit tests for the cookie-parsing utility."""

    def _req(self, cookie_value=None):
        rf = RequestFactory()
        req = rf.get('/')
        req.COOKIES = {}
        if cookie_value is not None:
            req.COOKIES['docFilters'] = cookie_value
        return req

    def test_no_cookie_defaults_to_westminster(self):
        result = get_active_traditions(self._req())
        assert result == ['westminster']

    def test_westminster_only(self):
        raw = json.dumps({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        result = get_active_traditions(self._req(raw))
        assert result == ['westminster']

    def test_tfu_only(self):
        raw = json.dumps({'westminster': False, 'three_forms_of_unity': True, 'other': False})
        result = get_active_traditions(self._req(raw))
        assert result == ['three_forms_of_unity']

    def test_multiple_traditions(self):
        raw = json.dumps({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        result = get_active_traditions(self._req(raw))
        assert set(result) == {'westminster', 'three_forms_of_unity'}

    def test_both_traditions(self):
        raw = json.dumps({'westminster': True, 'three_forms_of_unity': True})
        result = get_active_traditions(self._req(raw))
        assert set(result) == {'westminster', 'three_forms_of_unity'}

    def test_invalid_json_falls_back(self):
        result = get_active_traditions(self._req('not-valid-json'))
        assert result == ['westminster']

    def test_all_false_falls_back(self):
        raw = json.dumps({'westminster': False, 'three_forms_of_unity': False, 'other': False})
        result = get_active_traditions(self._req(raw))
        assert result == ['westminster']

    def test_empty_string_falls_back(self):
        result = get_active_traditions(self._req(''))
        assert result == ['westminster']


# ─── 8.2  View filter tests ──────────────────────────────────────────────────

@pytest.fixture
def wsc_cat(db):
    cat = Catechism.objects.get(slug='wsc')
    cat.total_questions = 5
    cat.save()
    return cat


@pytest.fixture
def tfu_cat(db):
    return CatechismFactory(
        name='Heidelberg Catechism',
        abbreviation='HC',
        slug='hc',
        total_questions=5,
        tradition=Catechism.THREE_FORMS_OF_UNITY,
    )


@pytest.fixture
def wsc_question(wsc_cat):
    topic = TopicFactory(catechism=wsc_cat, question_start=1, question_end=5)
    return QuestionFactory(
        catechism=wsc_cat, number=1, topic=topic,
        question_text='What is the chief end of man?',
        answer_text='To glorify God.',
    )


@pytest.fixture
def tfu_question(tfu_cat):
    topic = TopicFactory(catechism=tfu_cat, question_start=1, question_end=5)
    return QuestionFactory(
        catechism=tfu_cat, number=1, topic=topic,
        question_text='What is your only comfort?',
        answer_text='That I belong to Christ.',
    )


@pytest.mark.django_db
class TestSearchViewFilter:

    def test_westminster_only_cookie_excludes_tfu(self, wsc_question, tfu_question):
        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = c.get('/search/?q=comfort')
        assert resp.status_code == 200
        assert len(resp.context['results']) == 0

    def test_tfu_only_cookie_excludes_westminster(self, wsc_question, tfu_question):
        c = client_with_cookie({'westminster': False, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/search/?q=comfort')
        assert resp.status_code == 200
        assert len(resp.context['results']) == 1
        assert resp.context['results'][0].catechism.tradition == Catechism.THREE_FORMS_OF_UNITY

    def test_both_traditions_returns_all(self, wsc_question, tfu_question):
        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/search/?q=God')
        assert resp.status_code == 200
        traditions = {r.catechism.tradition for r in resp.context['results']}
        assert Catechism.WESTMINSTER in traditions

    def test_no_cookie_defaults_to_westminster(self, wsc_question, tfu_question):
        resp = Client().get('/search/?q=comfort')
        assert resp.status_code == 200
        assert len(resp.context['results']) == 0


@pytest.mark.django_db
class TestScriptureIndexViewFilter:

    def test_citation_count_filtered_by_tradition(self, wsc_question, tfu_question):
        book = BibleBookFactory(name='Romans', slug='romans-filter',
                                abbreviation='Rom', book_number=45, testament='NT')
        ScriptureIndexFactory(question=wsc_question, book=book, reference='Romans 1:1')
        ScriptureIndexFactory(question=tfu_question, book=book, reference='Romans 1:2')

        wsc_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = wsc_client.get('/scripture/')
        assert resp.status_code == 200
        romans = next(b for b in resp.context['nt_books'] if b.slug == 'romans-filter')
        assert romans.citation_count == 1

        both_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = both_client.get('/scripture/')
        romans = next(b for b in resp.context['nt_books'] if b.slug == 'romans-filter')
        assert romans.citation_count == 2


@pytest.mark.django_db
class TestScriptureBookViewFilter:

    def test_only_active_tradition_entries_shown(self, wsc_question, tfu_question):
        book = BibleBookFactory(name='John', slug='john-filter',
                                abbreviation='Jn', book_number=43, testament='NT')
        ScriptureIndexFactory(question=wsc_question, book=book, reference='John 3:16')
        ScriptureIndexFactory(question=tfu_question, book=book, reference='John 1:1')

        wsc_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = wsc_client.get('/scripture/john-filter/')
        assert resp.status_code == 200
        assert resp.context['total_citations'] == 1
        # Only WSC abbreviation in grouped entries
        assert 'HC' not in resp.context['grouped_entries']

    def test_all_traditions_shows_all(self, wsc_question, tfu_question):
        book = BibleBookFactory(name='Luke', slug='luke-filter',
                                abbreviation='Lk', book_number=42, testament='NT')
        ScriptureIndexFactory(question=wsc_question, book=book, reference='Luke 1:1')
        ScriptureIndexFactory(question=tfu_question, book=book, reference='Luke 1:2')

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/scripture/luke-filter/')
        assert resp.context['total_citations'] == 2


@pytest.fixture
def other_cat(db):
    return CatechismFactory(
        name='1689 Baptist Confession',
        abbreviation='1689',
        slug='1689',
        total_questions=5,
        tradition=Catechism.OTHER,
    )


@pytest.mark.django_db
class TestCompareIndexExcludesOtherTradition:
    """Sets containing catechisms with tradition='other' must never appear."""

    def test_set_with_other_tradition_hidden_from_index(self, wsc_cat, other_cat):
        cs = ComparisonSetFactory(name='Baptist Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=theme, catechism=other_cat, question_start=1, question_end=1)

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/compare/')
        assert resp.status_code == 200
        set_slugs = [s.slug for s in resp.context['comparison_sets']]
        assert '1689-baptist' not in set_slugs

    def test_set_with_only_active_traditions_shown(self, wsc_cat, tfu_cat):
        cs = ComparisonSetFactory(name='W+TFU Set', slug='w-tfu', order=11)
        theme = ComparisonThemeFactory(name='Both', slug='both', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=theme, catechism=tfu_cat, question_start=1, question_end=1)

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/compare/')
        set_slugs = [s.slug for s in resp.context['comparison_sets']]
        assert 'w-tfu' in set_slugs

    def test_direct_url_to_other_set_returns_404(self, wsc_cat, other_cat):
        cs = ComparisonSetFactory(name='Baptist Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=theme, catechism=other_cat, question_start=1, question_end=1)

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/compare/1689-baptist/')
        assert resp.status_code == 404

    def test_direct_url_to_other_theme_returns_404(self, wsc_cat, other_cat):
        cs = ComparisonSetFactory(name='Baptist Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=theme, catechism=other_cat, question_start=1, question_end=1)

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/compare/1689-baptist/scripture/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestCompareSetViewFilter:

    def test_themes_with_only_inactive_tradition_hidden(self, wsc_question, tfu_question, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        tfu_theme = ComparisonThemeFactory(
            name='TFU Only Theme', slug='tfu-only-theme', comparison_set=cs
        )
        ComparisonEntryFactory(
            theme=tfu_theme, catechism=tfu_question.catechism,
            question_start=1, question_end=1,
        )

        wsc_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = wsc_client.get('/compare/westminster/')
        assert resp.status_code == 200
        theme_slugs = [t.slug for t in resp.context['themes']]
        assert 'tfu-only-theme' not in theme_slugs

    def test_westminster_theme_visible_with_westminster_active(self, wsc_question, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        wsc_theme = ComparisonThemeFactory(
            name='WSC Theme', slug='wsc-theme', comparison_set=cs
        )
        ComparisonEntryFactory(
            theme=wsc_theme, catechism=wsc_question.catechism,
            question_start=1, question_end=1,
        )

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = c.get('/compare/westminster/')
        theme_slugs = [t.slug for t in resp.context['themes']]
        assert 'wsc-theme' in theme_slugs


@pytest.mark.django_db
class TestCompareSetThemeViewFilter:

    def test_columns_filtered_to_active_traditions(self, wsc_question, tfu_question, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(name='Mixed Theme', slug='mixed-theme', comparison_set=cs)
        ComparisonEntryFactory(
            theme=theme, catechism=wsc_question.catechism, question_start=1, question_end=1
        )
        ComparisonEntryFactory(
            theme=theme, catechism=tfu_question.catechism, question_start=1, question_end=1
        )

        wsc_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = wsc_client.get('/compare/westminster/mixed-theme/')
        assert resp.status_code == 200
        col_abbrs = [col['catechism'].abbreviation for col in resp.context['columns']]
        assert 'HC' not in col_abbrs
        assert wsc_question.catechism.abbreviation in col_abbrs

    def test_both_traditions_shows_both_columns(self, wsc_question, tfu_question, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(name='Both Theme', slug='both-theme', comparison_set=cs)
        ComparisonEntryFactory(
            theme=theme, catechism=wsc_question.catechism, question_start=1, question_end=1
        )
        ComparisonEntryFactory(
            theme=theme, catechism=tfu_question.catechism, question_start=1, question_end=1
        )

        c = client_with_cookie({'westminster': True, 'three_forms_of_unity': True, 'other': False})
        resp = c.get('/compare/westminster/both-theme/')
        assert len(resp.context['columns']) == 2


@pytest.mark.django_db
class TestQuestionPreviewFilter:

    def test_inactive_tradition_returns_404(self, tfu_question):
        wsc_client = client_with_cookie({'westminster': True, 'three_forms_of_unity': False, 'other': False})
        resp = wsc_client.get(f'/api/question/{tfu_question.pk}/preview/')
        assert resp.status_code == 404

    def test_active_tradition_returns_200(self, tfu_question):
        c = client_with_cookie({'westminster': False, 'three_forms_of_unity': True, 'other': False})
        resp = c.get(f'/api/question/{tfu_question.pk}/preview/')
        assert resp.status_code == 200

    def test_westminster_question_default_cookie_returns_200(self, wsc_question):
        resp = Client().get(f'/api/question/{wsc_question.pk}/preview/')
        assert resp.status_code == 200


@pytest.mark.django_db
class TestSitemapMatchesGatedSets:
    """The sitemap must not advertise URLs the comparison views gate off.

    Regression: a theme in an unsupported set whose own entries happen to be
    all-supported (the 1689 set's "Of Church Government", where the 1689 and
    Savoy ranges are null) passed the per-theme tradition filter and was listed
    in the sitemap, while CompareSetThemeView 404s every theme in that set.
    Search engines indexed /compare/1689-baptist/of-church-government/ and got
    a 404.
    """

    def _gated_set_with_westminster_only_theme(self, wsc_cat, other_cat):
        cs = ComparisonSetFactory(name='Baptist Lineage', slug='1689-baptist', order=10)
        # A theme whose 1689/Savoy ranges were null: only a Westminster entry.
        westminster_only = ComparisonThemeFactory(
            name='Of Church Government', slug='of-church-government', comparison_set=cs,
        )
        ComparisonEntryFactory(
            theme=westminster_only, catechism=wsc_cat, question_start=1, question_end=1,
        )
        # A sibling theme in the same set that does reference the 1689 text.
        mixed = ComparisonThemeFactory(
            name='Scripture', slug='of-the-holy-scriptures', comparison_set=cs,
        )
        ComparisonEntryFactory(theme=mixed, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=mixed, catechism=other_cat, question_start=1, question_end=1)
        return westminster_only

    def test_theme_in_gated_set_absent_from_sitemap(self, wsc_cat, other_cat):
        self._gated_set_with_westminster_only_theme(wsc_cat, other_cat)

        resp = Client().get('/sitemap.xml')
        assert resp.status_code == 200
        assert '/compare/1689-baptist/of-church-government/' not in resp.content.decode()

    def test_theme_in_gated_set_still_404s(self, wsc_cat, other_cat):
        self._gated_set_with_westminster_only_theme(wsc_cat, other_cat)

        assert Client().get('/compare/1689-baptist/of-church-government/').status_code == 404

    def test_every_comparison_url_in_sitemap_resolves(self, wsc_cat, other_cat):
        self._gated_set_with_westminster_only_theme(wsc_cat, other_cat)
        # A reachable set alongside the gated one.
        cs = ComparisonSetFactory(name='Westminster', slug='westminster-set', order=1)
        theme = ComparisonThemeFactory(name='Faith', slug='faith', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)

        c = Client()
        body = c.get('/sitemap.xml').content.decode()
        paths = re.findall(r'<loc>[^<]*?(/(?:compare|doctrine)/[^<]*)</loc>', body)
        assert paths, 'sitemap should advertise at least one comparison URL'
        assert [p for p in paths if c.get(p).status_code != 200] == []


@pytest.fixture
def confession_cat(db):
    """A document in the newly published 'reformed_confessions' collection."""
    return CatechismFactory(
        name='1689 London Baptist Confession',
        abbreviation='1689',
        slug='1689',
        total_questions=5,
        tradition=Catechism.REFORMED_CONFESSIONS,
    )


@pytest.mark.django_db
class TestReformedConfessionsArePublished:
    """The 1689, Savoy, Scots, Second Helvetic and Irish Articles were loaded
    with tradition='other', which every view gates on — so they and their two
    comparison sets were unreachable. They now form their own collection."""

    def _lineage_set(self, wsc_cat, confession_cat):
        cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(
            name='Of the Holy Scriptures', slug='of-the-holy-scriptures', comparison_set=cs,
        )
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)
        ComparisonEntryFactory(theme=theme, catechism=confession_cat, question_start=1, question_end=1)
        return cs, theme

    def test_reformed_confessions_is_a_valid_tradition(self):
        from catechism.utils import VALID_TRADITIONS
        assert 'reformed_confessions' in VALID_TRADITIONS

    def test_lineage_theme_page_no_longer_404s(self, wsc_cat, confession_cat):
        self._lineage_set(wsc_cat, confession_cat)

        c = client_with_cookie({
            'westminster': True, 'three_forms_of_unity': False, 'reformed_confessions': True,
        })
        resp = c.get('/compare/1689-baptist/of-the-holy-scriptures/')
        assert resp.status_code == 200
        assert {col['catechism'].slug for col in resp.context['columns']} == {'wsc', '1689'}

    def test_lineage_set_appears_in_the_index_when_enabled(self, wsc_cat, confession_cat):
        self._lineage_set(wsc_cat, confession_cat)

        c = client_with_cookie({
            'westminster': True, 'three_forms_of_unity': False, 'reformed_confessions': True,
        })
        assert '1689-baptist' in [s.slug for s in c.get('/compare/').context['comparison_sets']]

    def test_documents_without_a_parallel_are_named(self, wsc_cat, confession_cat):
        cs, _ = self._lineage_set(wsc_cat, confession_cat)
        # A theme the 1689 has no chapter for: only the Westminster entry.
        theme = ComparisonThemeFactory(
            name='Of Church Government', slug='of-church-government', comparison_set=cs,
        )
        ComparisonEntryFactory(theme=theme, catechism=wsc_cat, question_start=1, question_end=1)

        c = client_with_cookie({
            'westminster': True, 'three_forms_of_unity': False, 'reformed_confessions': True,
        })
        resp = c.get('/compare/1689-baptist/of-church-government/')
        assert resp.status_code == 200
        assert [d.slug for d in resp.context['documents_without_entry']] == ['1689']
        assert 'No parallel here' in resp.content.decode()


@pytest.mark.django_db
class TestComparisonColumnOrder:
    """Lineage sets are read left-to-right, so the oldest document comes first.

    The default ordering is alphabetical by abbreviation, which would put the
    1689 before the 1646 Confession it revises.
    """

    def test_columns_are_ordered_by_year(self, db):
        wcf = CatechismFactory(
            name='Westminster Confession', abbreviation='WCF', slug='wcf',
            year=1646, total_questions=5, tradition=Catechism.WESTMINSTER,
        )
        savoy = CatechismFactory(
            name='Savoy Declaration', abbreviation='Savoy', slug='savoy',
            year=1658, total_questions=5, tradition=Catechism.REFORMED_CONFESSIONS,
        )
        lbc = CatechismFactory(
            name='1689 London Baptist Confession', abbreviation='1689', slug='1689',
            year=1689, total_questions=5, tradition=Catechism.REFORMED_CONFESSIONS,
        )
        cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
        for cat in (lbc, savoy, wcf):        # inserted out of order on purpose
            ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=1)

        c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
        resp = c.get('/compare/1689-baptist/scripture/')
        assert [col['catechism'].slug for col in resp.context['columns']] == ['wcf', 'savoy', '1689']


@pytest.mark.django_db
class TestSitemapAdvertisesOnlyAnonymouslyVisibleThemes:
    """A crawler sends no docFilters cookie, so it sees DEFAULT_TRADITIONS.

    Regression: a theme whose only entries are outside the default collection
    (e.g. "Of the Gospel", carried by the 1689 and Savoy but not the
    Confession) was advertised from a sitemap built over every valid
    tradition, and 404'd for the crawler that followed the link.
    """

    def test_theme_outside_the_default_collection_is_not_advertised(self, wsc_cat, confession_cat):
        cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=10)
        westminster_theme = ComparisonThemeFactory(
            name='Of the Holy Scriptures', slug='of-the-holy-scriptures', comparison_set=cs,
        )
        ComparisonEntryFactory(
            theme=westminster_theme, catechism=wsc_cat, question_start=1, question_end=1,
        )
        confession_only = ComparisonThemeFactory(
            name='Of the Gospel', slug='of-the-gospel', comparison_set=cs,
        )
        ComparisonEntryFactory(
            theme=confession_only, catechism=confession_cat, question_start=1, question_end=1,
        )

        anon = Client()          # no cookie: exactly what a crawler sends
        body = anon.get('/sitemap.xml').content.decode()
        assert '/doctrine/of-the-gospel/' not in body
        assert anon.get('/doctrine/of-the-gospel/').status_code == 404
        # ...but it is reachable once the collection is enabled.
        enabled = client_with_cookie({'westminster': True, 'reformed_confessions': True})
        assert enabled.get('/doctrine/of-the-gospel/').status_code == 200

    def test_every_sitemap_url_resolves_for_an_anonymous_crawler(self, wsc_cat, confession_cat):
        cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=10)
        theme = ComparisonThemeFactory(
            name='Of the Gospel', slug='of-the-gospel', comparison_set=cs,
        )
        ComparisonEntryFactory(theme=theme, catechism=confession_cat, question_start=1, question_end=1)
        westminster_theme = ComparisonThemeFactory(
            name='Of the Holy Scriptures', slug='of-the-holy-scriptures', comparison_set=cs,
        )
        ComparisonEntryFactory(
            theme=westminster_theme, catechism=wsc_cat, question_start=1, question_end=1,
        )

        anon = Client()
        body = anon.get('/sitemap.xml').content.decode()
        paths = [urlparse(loc).path for loc in re.findall(r'<loc>([^<]+)</loc>', body)]
        assert paths
        assert [p for p in paths if anon.get(p).status_code != 200] == []
