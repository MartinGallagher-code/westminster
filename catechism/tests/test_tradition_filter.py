"""
Tests for the site-wide tradition filter:
  - get_active_traditions() utility (Phase 1)
  - Filtered view querysets (Phases 2-6)
"""
import json

import pytest
from django.test import Client, RequestFactory

from catechism.models import Catechism, ComparisonSet
from catechism.utils import get_active_traditions
from .conftest import (
    CatechismFactory, TopicFactory, QuestionFactory,
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

    def test_all_traditions(self):
        raw = json.dumps({'westminster': True, 'three_forms_of_unity': True, 'other': True})
        result = get_active_traditions(self._req(raw))
        assert set(result) == {'westminster', 'three_forms_of_unity', 'other'}

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
