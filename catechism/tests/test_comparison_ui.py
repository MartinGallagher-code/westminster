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
