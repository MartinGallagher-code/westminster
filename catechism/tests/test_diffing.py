"""Word-level diff between parallel sections of related confessions."""

import json

import pytest
from django.test import Client

from catechism.diffing import (
    DELETED, EQUAL, INSERTED, align_sections, change_ratio, diff_words,
)
from catechism.models import Catechism
from .conftest import (
    CatechismFactory, ComparisonEntryFactory, ComparisonSetFactory,
    ComparisonThemeFactory, QuestionFactory, TopicFactory,
)


def ops(segments):
    return [op for op, _text in segments]


def test_identical_text_is_all_equal():
    segments = diff_words('The Holy Scripture is the rule.', 'The Holy Scripture is the rule.')
    assert ops(segments) == [EQUAL]
    assert change_ratio(segments) == 0.0


def test_an_addition_is_marked_as_inserted():
    segments = diff_words('the rule of faith', 'the rule of faith and obedience')
    assert INSERTED in ops(segments)
    assert 'and obedience' in ''.join(t for op, t in segments if op == INSERTED)


def test_a_removal_is_marked_as_deleted():
    segments = diff_words('maintain piety, justice, and peace', 'maintain justice, and peace')
    assert DELETED in ops(segments)
    assert 'piety' in ''.join(t for op, t in segments if op == DELETED)


def test_punctuation_and_case_changes_are_ignored():
    """The editions modernised these freely; flagging them would bury the
    substantive edits under noise."""
    segments = diff_words(
        'knowledge, faith, and obedience.',
        'Knowledge, Faith and Obedience;',
    )
    assert ops(segments) == [EQUAL]


def test_change_ratio_reflects_how_much_moved():
    unchanged = diff_words('a b c d', 'a b c d')
    partly = diff_words('a b c d', 'a b c z')
    assert change_ratio(unchanged) == 0.0
    assert 0 < change_ratio(partly) < 1.0


def test_empty_input_is_handled():
    assert diff_words('', '') == []
    assert ops(diff_words('', 'added text')) == [INSERTED]
    assert ops(diff_words('removed text', '')) == [DELETED]


def test_alignment_pads_the_shorter_side():
    """A section one edition has and the other lacks is itself the difference."""
    pairs = align_sections(['a', 'b', 'c', 'd'], ['a', 'b', 'c'])
    assert pairs[-1] == ('d', None)
    assert len(pairs) == 4


@pytest.fixture
def lineage_theme(db):
    wcf = CatechismFactory(
        name='Westminster Confession', abbreviation='WCF', slug='wcf', year=1646,
        total_questions=2, tradition=Catechism.WESTMINSTER,
        document_type=Catechism.CONFESSION,
    )
    lbc = CatechismFactory(
        name='1689 London Baptist Confession', abbreviation='1689', slug='1689',
        year=1689, total_questions=2, tradition=Catechism.REFORMED_CONFESSIONS,
        document_type=Catechism.CONFESSION,
    )
    for catechism, text in ((wcf, 'maintain piety, justice, and peace'),
                            (lbc, 'maintain justice, and peace')):
        topic = TopicFactory(catechism=catechism, question_start=1, question_end=1)
        QuestionFactory(
            catechism=catechism, topic=topic, number=1,
            question_text='', answer_text=text,
        )
    cs = ComparisonSetFactory(name='Confessional Lineage', slug='1689-baptist', order=1)
    theme = ComparisonThemeFactory(
        name='Of the Civil Magistrate', slug='of-the-civil-magistrate', comparison_set=cs,
    )
    ComparisonEntryFactory(theme=theme, catechism=wcf, question_start=1, question_end=1)
    ComparisonEntryFactory(theme=theme, catechism=lbc, question_start=1, question_end=1)
    return theme


def enabled_client():
    client = Client()
    client.cookies['docFilters'] = json.dumps(
        {'westminster': True, 'reformed_confessions': True}
    )
    return client


@pytest.mark.django_db
def test_diff_page_shows_what_changed(lineage_theme):
    resp = enabled_client().get('/compare/1689-baptist/of-the-civil-magistrate/diff/')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert 'piety' in body
    assert '<del class="diff-del">' in body
    assert resp.context['changed_rows'] == 1


@pytest.mark.django_db
def test_the_older_edition_is_the_default_left_hand_side(lineage_theme):
    resp = enabled_client().get('/compare/1689-baptist/of-the-civil-magistrate/diff/')
    assert resp.context['left'].slug == 'wcf'
    assert resp.context['right'].slug == '1689'


@pytest.mark.django_db
def test_the_two_sides_can_be_swapped(lineage_theme):
    resp = enabled_client().get(
        '/compare/1689-baptist/of-the-civil-magistrate/diff/?a=1689&b=wcf'
    )
    assert resp.context['left'].slug == '1689'
    assert resp.context['right'].slug == 'wcf'


@pytest.mark.django_db
def test_asking_to_diff_a_document_against_itself_picks_another(lineage_theme):
    resp = enabled_client().get(
        '/compare/1689-baptist/of-the-civil-magistrate/diff/?a=wcf&b=wcf'
    )
    assert resp.context['left'] != resp.context['right']


@pytest.mark.django_db
def test_one_document_in_the_active_collections_is_not_a_comparison(lineage_theme):
    westminster_only = Client()
    westminster_only.cookies['docFilters'] = json.dumps({'westminster': True})
    resp = westminster_only.get('/compare/1689-baptist/of-the-civil-magistrate/diff/')
    assert resp.status_code == 200
    assert resp.context['error']


@pytest.mark.django_db
def test_the_theme_page_links_to_the_diff(lineage_theme):
    body = enabled_client().get('/compare/1689-baptist/of-the-civil-magistrate/').content.decode()
    assert '/compare/1689-baptist/of-the-civil-magistrate/diff/' in body
