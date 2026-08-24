"""The comparison offer on a chapter page.

A reader on WCF XXV had no way of knowing the Savoy and the 1689 rewrite that
chapter unless they went looking in the comparison index first. The data was
always there; these tests pin down that the chapter itself now says so.
"""

import json

import pytest
from django.test import Client

from catechism.models import Catechism
from catechism.views import (
    _comparison_themes_for_topic, _dormant_comparison_traditions,
)
from .conftest import (
    CatechismFactory, ComparisonEntryFactory, ComparisonSetFactory,
    ComparisonThemeFactory, QuestionFactory, TopicFactory,
)

WESTMINSTER_ONLY = {'westminster': True}
BOTH = {'westminster': True, 'reformed_confessions': True}


def client_with(filters):
    client = Client()
    client.cookies['docFilters'] = json.dumps(filters)
    return client


def confession(name, abbreviation, slug, year, tradition):
    return CatechismFactory(
        name=name, abbreviation=abbreviation, slug=slug, year=year,
        total_questions=6, tradition=tradition,
        document_type=Catechism.CONFESSION,
    )


def chapter(catechism, slug, order, start, end, text='the same words'):
    topic = TopicFactory(
        catechism=catechism, name=f'Chapter {order}', slug=slug, order=order,
        question_start=start, question_end=end,
    )
    for number in range(start, end + 1):
        QuestionFactory(
            catechism=catechism, topic=topic, number=number,
            question_text='', answer_text=text,
        )
    return topic


@pytest.fixture
def lineage(db):
    """WCF and the 1689, with one theme covering a chapter of each.

    The 1689 folds two Westminster chapters into one, so its entry spans a
    range that both WCF chapters overlap — the case the overlap test exists
    for.
    """
    wcf = confession('Westminster Confession', 'WCF', 'wcf', 1646, Catechism.WESTMINSTER)
    lbc = confession(
        '1689 London Baptist Confession', '1689', '1689', 1689,
        Catechism.REFORMED_CONFESSIONS,
    )
    church = chapter(wcf, 'of-the-church', 25, 1, 2, 'the visible Church')
    chapter(wcf, 'of-communion', 26, 3, 4, 'communion of saints')
    lbc_chapter = chapter(lbc, 'of-the-church', 26, 1, 4, 'the visible church')

    comparison_set = ComparisonSetFactory(
        name='Confessional Lineage', slug='1689-baptist', order=1,
    )
    theme = ComparisonThemeFactory(
        name='Of the Church', slug='of-the-church', comparison_set=comparison_set,
    )
    ComparisonEntryFactory(theme=theme, catechism=wcf, question_start=1, question_end=4)
    ComparisonEntryFactory(theme=theme, catechism=lbc, question_start=1, question_end=4)
    return {
        'wcf': wcf, '1689': lbc, 'theme': theme,
        'church': church, 'lbc_chapter': lbc_chapter,
    }


@pytest.mark.django_db
def test_a_chapter_finds_the_theme_that_covers_it(lineage):
    themes = _comparison_themes_for_topic(lineage['church'], ['westminster', 'reformed_confessions'])
    assert [theme.slug for theme in themes] == ['of-the-church']


@pytest.mark.django_db
def test_both_halves_of_a_merged_chapter_find_the_same_theme(lineage):
    """The 1689's chapter 26 answers WCF XXV and XXVI together; asking from
    either Westminster chapter has to reach it."""
    for slug in ('of-the-church', 'of-communion'):
        topic = lineage['wcf'].topics.get(slug=slug)
        themes = _comparison_themes_for_topic(topic, ['westminster', 'reformed_confessions'])
        assert [theme.slug for theme in themes] == ['of-the-church'], slug


@pytest.mark.django_db
def test_a_theme_with_only_one_active_document_is_not_offered(lineage):
    """With the Reformed Confessions switched off the only entry left is this
    document's own — there is nothing to compare it against."""
    assert _comparison_themes_for_topic(lineage['church'], ['westminster']) == []


@pytest.mark.django_db
def test_the_chapter_page_offers_the_comparison(lineage):
    body = client_with(BOTH).get('/wcf/chapters/of-the-church/').content.decode()
    assert '/compare/1689-baptist/of-the-church/' in body
    assert 'Compare side by side' in body


@pytest.mark.django_db
def test_the_chapter_page_links_the_word_level_diff(lineage):
    body = client_with(BOTH).get('/wcf/chapters/of-the-church/').content.decode()
    assert '/compare/1689-baptist/of-the-church/diff/?a=wcf&amp;b=1689' in body


@pytest.mark.django_db
def test_the_offer_names_the_other_documents(lineage):
    resp = client_with(BOTH).get('/wcf/chapters/of-the-church/')
    assert [c.slug for c in resp.context['primary_comparison_documents']] == ['1689']


@pytest.mark.django_db
def test_a_switched_off_collection_is_named_rather_than_hidden(lineage):
    resp = client_with(WESTMINSTER_ONLY).get('/wcf/chapters/of-the-church/')
    assert resp.context['comparison_themes'] == []
    dormant = resp.context['dormant_comparison_traditions']
    assert [row['tradition'] for row in dormant] == ['reformed_confessions']
    assert [c.abbreviation for c in dormant[0]['documents']] == ['1689']
    body = resp.content.decode()
    assert 'Turn on Reformed Confessions to compare' in body
    assert 'data-tradition="reformed_confessions"' in body


@pytest.mark.django_db
def test_nothing_is_dormant_once_every_collection_is_on(lineage):
    resp = client_with(BOTH).get('/wcf/chapters/of-the-church/')
    assert resp.context['dormant_comparison_traditions'] == []


@pytest.mark.django_db
def test_a_chapter_no_theme_covers_offers_nothing(lineage):
    lonely = confession('Irish Articles', 'IAR', 'irish', 1615, Catechism.REFORMED_CONFESSIONS)
    topic = chapter(lonely, 'of-the-scriptures', 1, 1, 2)
    resp = client_with(BOTH).get('/irish/chapters/of-the-scriptures/')
    assert resp.context['comparison_themes'] == []
    assert resp.context['dormant_comparison_traditions'] == []
    assert 'chapter-compare-panel' not in resp.content.decode()
    assert topic.catechism == lonely


@pytest.mark.django_db
def test_the_diff_is_only_offered_against_the_same_kind_of_document(db):
    """A confession chapter beside a catechism answer is a fair comparison but
    not a fair diff: every word would come back changed."""
    wcf = confession('Westminster Confession', 'WCF', 'wcf', 1646, Catechism.WESTMINSTER)
    wsc = CatechismFactory(
        name='Shorter Catechism', abbreviation='SC-T', slug='wsc-test', year=1647,
        total_questions=3, tradition=Catechism.WESTMINSTER,
        document_type=Catechism.CATECHISM,
    )
    chapter(wcf, 'of-god', 2, 1, 2, 'There is but one only living and true God')
    chapter(wsc, 'god', 1, 1, 2, 'God is a Spirit, infinite, eternal')

    comparison_set = ComparisonSetFactory(name='Standards', slug='standards-test', order=0)
    theme = ComparisonThemeFactory(
        name='God', slug='god-and-the-holy-trinity', comparison_set=comparison_set,
    )
    ComparisonEntryFactory(theme=theme, catechism=wcf, question_start=1, question_end=2)
    ComparisonEntryFactory(theme=theme, catechism=wsc, question_start=1, question_end=2)

    resp = client_with(WESTMINSTER_ONLY).get('/wcf/chapters/of-god/')
    assert resp.context['primary_comparison_theme'].slug == 'god-and-the-holy-trinity'
    assert resp.context['primary_comparison_diff_target'] is None
    assert 'See what changed' not in resp.content.decode()


@pytest.mark.django_db
def test_the_theme_covering_most_of_the_chapter_leads(db):
    """A theme that clips the chapter's last section must not outrank one that
    treats the whole of it."""
    wcf = confession('Westminster Confession', 'WCF', 'wcf', 1646, Catechism.WESTMINSTER)
    lbc = confession('1689', '1689', '1689', 1689, Catechism.REFORMED_CONFESSIONS)
    topic = chapter(wcf, 'of-the-church', 25, 1, 6)
    chapter(lbc, 'of-the-church', 26, 1, 6)

    comparison_set = ComparisonSetFactory(name='Lineage', slug='1689-baptist', order=1)
    partial = ComparisonThemeFactory(
        name='Partial', slug='partial', comparison_set=comparison_set, order=0,
    )
    whole = ComparisonThemeFactory(
        name='Whole', slug='whole', comparison_set=comparison_set, order=1,
    )
    for theme, end in ((partial, 2), (whole, 6)):
        ComparisonEntryFactory(theme=theme, catechism=wcf, question_start=1, question_end=end)
        ComparisonEntryFactory(theme=theme, catechism=lbc, question_start=1, question_end=end)

    themes = _comparison_themes_for_topic(topic, ['westminster', 'reformed_confessions'])
    assert [theme.slug for theme in themes] == ['whole', 'partial']


@pytest.mark.django_db
def test_a_dormant_collection_is_only_reported_when_turning_it_on_would_help(lineage):
    """Nothing is dormant for the 1689's own chapter when its collection is the
    one already on and the Westminster documents are too."""
    assert _dormant_comparison_traditions(
        lineage['lbc_chapter'], ['westminster', 'reformed_confessions'],
    ) == []
