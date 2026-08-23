"""Stable references ("WCF 3.4") and citation export."""

from datetime import date

import pytest

from catechism.citations import (
    bibtex, citation_key, citation_label, citation_text, resolve_reference, ris,
)
from catechism.models import Topic
from .conftest import QuestionFactory

ACCESSED = date(2026, 8, 23)


@pytest.fixture
def wcf_chapter3(confession):
    """A confession whose chapter 3 starts at section 14, as the real one does."""
    confession.year = 1646
    confession.save()
    chapter = Topic.objects.create(
        catechism=confession, name="Of God's Eternal Decree", slug='decree',
        order=3, question_start=14, question_end=21,
    )
    return QuestionFactory(
        catechism=confession, topic=chapter, number=17,
        question_text='These angels and men, thus predestinated and foreordained…',
    )


@pytest.mark.django_db
def test_a_confession_reference_resolves_through_its_chapter(confession, wcf_chapter3):
    # 3.4 is the fourth section of chapter 3 — section 17 overall.
    assert resolve_reference(confession, '3.4') == wcf_chapter3
    assert wcf_chapter3.display_number == '3.4'


@pytest.mark.django_db
def test_confession_references_need_a_section(confession, wcf_chapter3):
    assert resolve_reference(confession, '3') is None


@pytest.mark.django_db
def test_out_of_range_references_do_not_resolve(confession, wcf_chapter3):
    assert resolve_reference(confession, '99.1') is None
    assert resolve_reference(confession, '3.99') is None      # past question_end
    assert resolve_reference(confession, 'nonsense') is None
    assert resolve_reference(confession, '') is None


@pytest.mark.django_db
def test_a_catechism_reference_is_a_bare_number(catechism, question):
    assert resolve_reference(catechism, '1') == question
    assert resolve_reference(catechism, '1.1') is None


@pytest.mark.django_db
def test_citation_label_and_key(confession, wcf_chapter3):
    assert citation_label(wcf_chapter3) == 'WCF 3.4'
    assert citation_key(wcf_chapter3) == 'wcf-3-4'


@pytest.mark.django_db
def test_citation_text_names_the_document_and_part(confession, wcf_chapter3):
    text = citation_text(wcf_chapter3, 'https://example.test/cite/wcf/3.4/')
    assert 'Westminster Confession' in text
    assert '(1646)' in text
    assert 'Chapter 3, Section 4' in text
    assert 'https://example.test/cite/wcf/3.4/' in text


@pytest.mark.django_db
def test_bibtex_entry_is_well_formed(confession, wcf_chapter3):
    entry = bibtex(wcf_chapter3, 'https://example.test/cite/wcf/3.4/', ACCESSED)
    assert entry.startswith('@incollection{wcf-3-4,')
    assert entry.count('{') == entry.count('}')
    assert 'booktitle  = {{Westminster Confession of Faith}}' in entry
    assert 'urldate    = {2026-08-23}' in entry
    assert entry.rstrip().endswith('}')


@pytest.mark.django_db
def test_ris_record_is_well_formed(confession, wcf_chapter3):
    record = ris(wcf_chapter3, 'https://example.test/cite/wcf/3.4/', ACCESSED)
    assert record.startswith('TY  - CHAP')
    assert 'BT  - Westminster Confession of Faith' in record
    assert record.rstrip().endswith('ER  -')


@pytest.mark.django_db
def test_permalink_redirects_to_the_canonical_page(client, confession, wcf_chapter3):
    resp = client.get('/cite/wcf/3.4/')
    assert resp.status_code == 301
    assert resp['Location'] == wcf_chapter3.get_absolute_url() == '/wcf/sections/17/'


@pytest.mark.django_db
def test_unknown_permalink_is_404(client, confession, wcf_chapter3):
    assert client.get('/cite/wcf/9.9/').status_code == 404
    assert client.get('/cite/nope/3.4/').status_code == 404


@pytest.mark.django_db
def test_bibtex_download(client, confession, wcf_chapter3):
    resp = client.get('/cite/wcf/3.4/bibtex/')
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('application/x-bibtex')
    assert resp['Content-Disposition'] == 'attachment; filename="wcf-3-4.bib"'
    body = resp.content.decode()
    assert '@incollection{wcf-3-4,' in body
    # The exported URL is the permalink, not the sequential-number page.
    assert '/cite/wcf/3.4/' in body


@pytest.mark.django_db
def test_ris_download(client, confession, wcf_chapter3):
    resp = client.get('/cite/wcf/3.4/ris/')
    assert resp.status_code == 200
    assert resp['Content-Disposition'] == 'attachment; filename="wcf-3-4.ris"'
    assert 'TY  - CHAP' in resp.content.decode()


@pytest.mark.django_db
def test_unknown_format_is_404(client, confession, wcf_chapter3):
    assert client.get('/cite/wcf/3.4/endnote/').status_code == 404


@pytest.mark.django_db
def test_question_page_offers_the_citation_controls(client, confession, wcf_chapter3):
    body = client.get('/wcf/sections/17/').content.decode()
    assert '/cite/wcf/3.4/' in body
    assert '/cite/wcf/3.4/bibtex/' in body
    assert '/cite/wcf/3.4/ris/' in body
    assert 'Cite WCF 3.4' in body
