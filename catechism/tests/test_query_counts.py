"""Page cost must not grow with the size of the document.

Rendering a row asks it for its URL, and ``Question.get_absolute_url`` needs
the document's slug and type to pick a route. Every queryset that had not said
``select_related('catechism')`` therefore paid one query per row: a single
Larger Catechism question page issued 224 queries, 204 of them the same
``SELECT ... FROM catechism_catechism``. The document home pages were as bad.

Counting queries on one page would only pin the number down for the data that
test happens to build. These tests double the rows instead: the cost of a page
has to stay flat, which is the property that actually matters.
"""

import json

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from catechism.models import Catechism
from .conftest import CatechismFactory, QuestionFactory, TopicFactory


def build_chapter(sections):
    confession = CatechismFactory(
        name='Westminster Confession', abbreviation='WCF', slug='wcf', year=1646,
        total_questions=sections, tradition=Catechism.WESTMINSTER,
        document_type=Catechism.CONFESSION,
    )
    topic = TopicFactory(
        catechism=confession, name='Of the Holy Scripture', slug='of-the-holy-scripture',
        order=1, question_start=1, question_end=sections,
    )
    for number in range(1, sections + 1):
        QuestionFactory(
            catechism=confession, topic=topic, number=number,
            question_text='Of the Holy Scripture',
            answer_text=f'Section {number} of the chapter.',
        )
    return confession, topic


def count_queries(client, path):
    with CaptureQueriesContext(connection) as ctx:
        resp = client.get(path)
    assert resp.status_code == 200, f'{path} -> {resp.status_code}'
    # Django's DatabaseCache does its own bookkeeping, which varies with how
    # full the cache table is and says nothing about the page.
    return len([
        q for q in ctx.captured_queries
        if 'django_cache_table' not in q['sql']
    ])


def westminster_client():
    client = Client()
    client.cookies['docFilters'] = json.dumps({'westminster': True})
    return client


@pytest.mark.django_db
def test_a_chapter_page_costs_the_same_for_twice_the_sections():
    client = westminster_client()

    build_chapter(sections=4)
    small = count_queries(client, '/wcf/chapters/of-the-holy-scripture/')

    Catechism.objects.filter(slug='wcf').delete()
    build_chapter(sections=8)
    large = count_queries(client, '/wcf/chapters/of-the-holy-scripture/')

    assert large == small, (
        f'{small} queries for 4 sections but {large} for 8: the page is paying '
        f'per row. Something it renders is reaching through a relation the '
        f'queryset did not select_related.'
    )


@pytest.mark.django_db
def test_a_document_home_costs_the_same_for_twice_the_questions():
    client = westminster_client()

    build_chapter(sections=4)
    small = count_queries(client, '/wcf/')

    Catechism.objects.filter(slug='wcf').delete()
    build_chapter(sections=8)
    large = count_queries(client, '/wcf/')

    assert large == small, f'{small} queries for 4 questions but {large} for 8'


@pytest.mark.django_db
def test_the_document_map_survives_a_document_being_renamed():
    """The map is only safe because a save invalidates it."""
    confession, _topic = build_chapter(sections=2)
    question = confession.questions.first()
    assert question.get_absolute_url() == '/wcf/sections/1/'

    confession.slug = 'westminster-confession'
    confession.save()

    fresh = type(question).objects.get(pk=question.pk)
    assert fresh.get_absolute_url() == '/westminster-confession/sections/1/'


@pytest.mark.django_db
def test_the_document_map_notices_a_change_of_document_type():
    """Route choice depends on it: a confession's items are sections, a
    catechism's are questions."""
    confession, _topic = build_chapter(sections=2)
    question = confession.questions.first()
    assert '/sections/' in question.get_absolute_url()

    confession.document_type = Catechism.CATECHISM
    confession.save()

    fresh = type(question).objects.get(pk=question.pk)
    assert '/questions/' in fresh.get_absolute_url()


@pytest.mark.django_db
def test_a_loaded_document_is_preferred_over_the_map():
    """select_related must keep working — and keep being the faster path."""
    confession, _topic = build_chapter(sections=2)
    question = confession.questions.select_related('catechism').first()
    with CaptureQueriesContext(connection) as ctx:
        assert question.get_absolute_url() == '/wcf/sections/1/'
    assert len(ctx.captured_queries) == 0
