"""Recognising Scripture references typed into the search box."""

import pytest

from catechism.scripture_refs import (
    chapter_from_ref, parse_scripture_reference, reference_matches_chapter,
    scripture_urls,
)
from .conftest import BibleBookFactory, QuestionFactory


@pytest.fixture
def books(db):
    made = [
        ('Romans', 'Rom', 'romans', 45),
        ('1 Corinthians', '1 Cor', '1-corinthians', 46),
        ('Philippians', 'Phil', 'philippians', 50),
        ('Philemon', 'Phlm', 'philemon', 57),
        ('Job', 'Job', 'job', 18),
        ('Acts', 'Acts', 'acts', 44),
        ('Judges', 'Judg', 'judges', 7),
        ('Jude', 'Jude', 'jude', 65),
    ]
    return [
        BibleBookFactory(name=n, abbreviation=a, slug=s, book_number=num, testament='NT')
        for n, a, s, num in made
    ]


@pytest.mark.parametrize('query,expected', [
    ('Rom 8:30', 'Romans 8:30'),
    ('rom 8', 'Romans 8'),
    ('Rom. 8:30', 'Romans 8:30'),
    ('Romans 8:29-30', 'Romans 8:29-30'),
    ('1 Cor 13', '1 Corinthians 13'),
    ('1Cor 13:4', '1 Corinthians 13:4'),
    ('I Corinthians 13', '1 Corinthians 13'),
    ('Job 1:1', 'Job 1:1'),
])
def test_recognises_references(query, expected, books):
    assert parse_scripture_reference(query, books)['label'] == expected


@pytest.mark.parametrize('query', [
    'acts',                # a book name, but far more likely an English word
    'Romans',              # bare book name: no chapter, so not a reference
    'justification',
    'faith 101',           # no such book
    '',
])
def test_leaves_ordinary_queries_alone(query, books):
    assert parse_scripture_reference(query, books) is None


def test_exact_abbreviation_beats_an_ambiguous_prefix(books):
    # "Phil" prefixes both Philippians and Philemon, but it is Philippians'
    # actual abbreviation, so it resolves.
    assert parse_scripture_reference('Phil 3:9', books)['book'].slug == 'philippians'


def test_ambiguous_prefix_is_not_guessed(books):
    # "Jud" prefixes both Judges and Jude and abbreviates neither, so it is
    # left to the text search rather than guessed at.
    assert parse_scripture_reference('Jud 1', books) is None
    # The unambiguous forms still resolve.
    assert parse_scripture_reference('Judg 1', books)['book'].slug == 'judges'
    assert parse_scripture_reference('Jude 1', books)['book'].slug == 'jude'


def test_unique_prefix_resolves(books):
    # "Phili" prefixes Philippians only — Philemon is phil-e.
    assert parse_scripture_reference('Phili 3', books)['book'].slug == 'philippians'


@pytest.mark.parametrize('reference,chapter,matches', [
    ('Rom 8:29-30', 8, True),
    ('Romans 8', 8, True),
    ('8:30', 8, True),
    ('Rom 1:8', 8, False),      # 8 is the verse, not the chapter
    ('Rom 18:1', 8, False),     # 8 is part of 18
])
def test_reference_chapter_matching(reference, chapter, matches):
    assert reference_matches_chapter(reference, chapter) is matches


def test_chapter_from_ref():
    assert chapter_from_ref('8:30') == 8
    assert chapter_from_ref('8') == 8
    assert chapter_from_ref('') is None


@pytest.mark.django_db
def test_search_routes_a_reference_to_the_scripture_index(client, books):
    resp = client.get('/search/?q=Rom+8:30')
    assert resp.status_code == 302
    assert resp['Location'].startswith('/scripture/romans/')
    assert 'ref=8%3A30' in resp['Location']


@pytest.mark.django_db
def test_text_escape_hatch_keeps_the_substring_search(client, books):
    resp = client.get('/search/?q=Rom+8:30&text=1')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_ordinary_query_is_not_redirected(client, books):
    assert client.get('/search/?q=justification').status_code == 200


@pytest.mark.django_db
def test_scripture_book_page_notes_the_filter(client, books):
    resp = client.get('/scripture/romans/?ref=8:30&from=Rom+8:30')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert 'Romans 8:30' in body
    assert 'text=1' in body        # the escape hatch back to a text search


# ── Proof references as links ────────────────────────────────────────────
#
# Verse text comes from a manual fetch against an upstream service, so a loaded
# database usually has none. That used to leave every proof reference as a bold,
# clickable line whose collapse target was empty — a control that did nothing.
# The reference now links to the Scripture index instead.


def test_scripture_urls_links_a_plain_reference(books):
    urls = scripture_urls(['1 Cor. 10:31'], books=books)
    assert urls['1 Cor. 10:31'].startswith('/scripture/1-corinthians/')
    assert 'ref=10%3A31' in urls['1 Cor. 10:31']


def test_scripture_urls_carries_the_reference_as_written(books):
    url = scripture_urls(['Rom. 8:29-30'], books=books)['Rom. 8:29-30']
    assert 'from=Rom.+8%3A29-30' in url


@pytest.mark.parametrize('reference', [
    '1 Cor. 10:16, 17, 21',      # a verse list
    '1 Cor. 11:23 to 29',        # a spelled-out range
    '1 Cor. 11:27 to the end, with Jude 23',
    '1 Cor. 10:14-16,21',
])
def test_scripture_urls_falls_back_to_the_leading_citation(books, reference):
    """A multi-verse proof still lands the reader on the right chapter."""
    url = scripture_urls([reference], books=books)[reference]
    assert url.startswith('/scripture/1-corinthians/')
    assert 'ref=1' in url


@pytest.mark.parametrize('reference', [
    '10:43',            # no book — the chapter is inherited from a neighbour
    '1 Cor. 5 chap.',
])
def test_scripture_urls_omits_what_it_cannot_place(books, reference):
    """Unresolvable references get no entry, so the template renders plain text."""
    assert scripture_urls([reference], books=books) == {}


def test_scripture_urls_is_empty_for_no_references(books):
    assert scripture_urls([], books=books) == {}
    assert scripture_urls(None, books=books) == {}


@pytest.mark.django_db
def test_proof_reference_renders_as_a_link_without_verse_text(client, books):
    """The reference is actionable even when nothing has been fetched."""
    question = QuestionFactory(proof_texts='1 Cor. 10:31; Rom. 11:36')
    body = client.get(question.get_absolute_url()).content.decode()

    assert 'href="/scripture/1-corinthians/?ref=10%3A31' in body
    # The old dead affordance: a collapse toggle with an empty target.
    assert 'data-bs-target="#verse-' not in body


@pytest.mark.django_db
def test_unresolvable_proof_reference_is_not_a_link(client, books):
    question = QuestionFactory(proof_texts='10:43')
    body = client.get(question.get_absolute_url()).content.decode()

    assert '<span class="scripture-ref fw-bold">10:43</span>' in body
