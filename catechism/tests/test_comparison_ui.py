"""Comparison page chrome: the narrow-screen document switcher."""

import json

import pytest
from django.test import Client

from catechism.models import Catechism
from .conftest import (
    CatechismFactory, ComparisonEntryFactory, ComparisonSetFactory,
    ComparisonThemeFactory,
)


def client_with_cookie(filters):
    c = Client()
    c.cookies['docFilters'] = json.dumps(filters)
    return c


@pytest.fixture
def lineage(db):
    wcf = CatechismFactory(
        name='Westminster Confession', abbreviation='WCF', slug='wcf', year=1646,
        total_questions=5, tradition=Catechism.WESTMINSTER,
    )
    lbc = CatechismFactory(
        name='1689 London Baptist Confession', abbreviation='1689', slug='1689',
        year=1689, total_questions=5, tradition=Catechism.REFORMED_CONFESSIONS,
    )
    cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=10)
    both = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
    ComparisonEntryFactory(theme=both, catechism=wcf, question_start=1, question_end=1)
    ComparisonEntryFactory(theme=both, catechism=lbc, question_start=1, question_end=1)
    alone = ComparisonThemeFactory(name='Church Government', slug='polity', comparison_set=cs)
    ComparisonEntryFactory(theme=alone, catechism=wcf, question_start=1, question_end=1)
    return cs


@pytest.mark.django_db
def test_document_switcher_is_rendered_for_multi_column_comparisons(lineage):
    c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
    body = c.get('/compare/1689-baptist/scripture/').content.decode()

    assert 'comparison-doc-tabs' in body
    assert 'data-doc="wcf"' in body
    assert 'data-doc="1689"' in body
    assert 'role="group"' in body
    assert 'aria-pressed' in body


@pytest.mark.django_db
def test_no_document_switcher_when_there_is_only_one_column(lineage):
    c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
    body = c.get('/compare/1689-baptist/polity/').content.decode()

    assert 'comparison-doc-tabs' not in body


@pytest.mark.django_db
def test_switcher_comment_is_not_rendered_into_the_page(lineage):
    """Django only strips ``{# #}`` on a single line; a multi-line one leaks."""
    c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
    body = c.get('/compare/1689-baptist/scripture/').content.decode()

    assert 'Narrow-screen document switcher' not in body
    assert '{#' not in body


@pytest.fixture
def custom_pair(db):
    wcf = CatechismFactory(
        name='Westminster Confession', abbreviation='WCF', slug='wcf', year=1646,
        total_questions=5, tradition=Catechism.WESTMINSTER,
    )
    lbc = CatechismFactory(
        name='1689 London Baptist Confession', abbreviation='1689', slug='1689',
        year=1689, total_questions=5, tradition=Catechism.REFORMED_CONFESSIONS,
    )
    cs = ComparisonSetFactory(name='Lineage', slug='lineage', order=1)
    theme = ComparisonThemeFactory(name='Scripture', slug='scripture', comparison_set=cs)
    ComparisonEntryFactory(theme=theme, catechism=wcf, question_start=1, question_end=1)
    ComparisonEntryFactory(theme=theme, catechism=lbc, question_start=1, question_end=1)
    return wcf, lbc


@pytest.mark.django_db
class TestCustomComparisonsAreShareable:
    """The chosen documents live in ?docs=, so a link reproduces the view."""

    def test_a_pasted_link_reproduces_the_same_columns(self, custom_pair):
        cookie = {'westminster': True, 'reformed_confessions': True}
        url = '/compare/custom/scripture/?docs=wcf,1689'

        first = client_with_cookie(cookie).get(url)
        # A different visitor, no shared session, following the same link.
        second = client_with_cookie(cookie).get(url)

        assert first.status_code == second.status_code == 200
        assert (
            [col['catechism'].slug for col in first.context['columns']]
            == [col['catechism'].slug for col in second.context['columns']]
            == ['wcf', '1689']
        )

    def test_the_page_offers_a_copy_link_control(self, custom_pair):
        c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
        body = c.get('/compare/custom/scripture/?docs=wcf,1689').content.decode()
        assert 'data-copy="url"' in body
        assert 'Copy shareable link' in body

    def test_no_copy_control_before_a_selection_is_made(self, custom_pair):
        c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
        body = c.get('/compare/custom/').content.decode()
        assert 'data-copy="url"' not in body

    def test_theme_links_carry_the_selection_forward(self, custom_pair):
        c = client_with_cookie({'westminster': True, 'reformed_confessions': True})
        body = c.get('/compare/custom/?docs=wcf,1689').content.decode()
        assert '?docs=wcf,1689' in body
