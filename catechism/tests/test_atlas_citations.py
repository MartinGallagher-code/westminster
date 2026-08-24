"""Citing the Atlas itself.

The Standards' text was already citable — WCF 3.4 resolves to a permalink and
exports as BibTeX or RIS. The Atlas is a different kind of source: not a
historic document but a reference work making its own claims. A seminarian
citing its reading of the Sabbath crux, or its definition of
Hypothetical-Universal, had nothing to put in a footnote.
"""

import datetime

import pytest
from django.test import Client
from django.urls import reverse

from catechism.models import DataVersion
from westminster_standards import atlas_citations as citations
from westminster_standards.cruxes import CRUXES
from westminster_standards.glossary import VALUE_BY_KEYS
from westminster_standards.heads_of_doctrine import HEADS_OF_DOCTRINE
from westminster_standards.personas import PERSONAS
from westminster_standards.schools import SCHOOLS

A_POSITION = next(iter(VALUE_BY_KEYS.values()))
POSITION_REF = 'position/{dim_key}/{attr_key}/{value_key}'.format(**A_POSITION)


def refs():
    return [
        ('persona', f'persona/{PERSONAS[0]["slug"]}', PERSONAS[0]['name']),
        ('crux', f'crux/{CRUXES[0]["slug"]}', CRUXES[0]['title']),
        ('head', f'head/{HEADS_OF_DOCTRINE[0]["slug"]}', HEADS_OF_DOCTRINE[0]['name']),
        ('school', f'school/{SCHOOLS[0]["slug"]}', SCHOOLS[0]['name']),
        ('locus', 'locus/scripture', 'Scripture'),
        ('position', POSITION_REF, A_POSITION['label']),
        ('pair', 'pair/scripture-god_decree', 'Scripture × God & Decree'),
    ]


@pytest.mark.parametrize('kind,ref,title', refs(), ids=lambda v: str(v)[:30])
def test_every_kind_of_atlas_page_resolves_to_a_citation(kind, ref, title):
    entity = citations.resolve(ref)
    assert entity is not None, ref
    assert entity['title'] == title
    assert entity['ref'] == ref


@pytest.mark.django_db
@pytest.mark.parametrize('kind,ref,title', refs(), ids=lambda v: str(v)[:30])
def test_the_reference_points_at_the_page_it_names(kind, ref, title):
    """A citation whose URL 404s is worse than none; this is the check that
    the reference and the Atlas's own routing agree."""
    entity = citations.resolve(ref)
    resp = Client().get(entity['url'])
    assert resp.status_code == 200, entity['url']


@pytest.mark.parametrize('ref', [
    '', 'persona', 'persona/nobody-of-that-name', 'nonsense/thing',
    'position/scripture/sufficiency', 'locus/not-a-locus',
    'position/scripture/sufficiency/not-a-value',
])
def test_a_reference_the_ontology_does_not_hold_resolves_to_nothing(ref):
    assert citations.resolve(ref) is None


@pytest.mark.django_db
def test_the_permalink_redirects_to_the_page():
    ref = f'persona/{PERSONAS[0]["slug"]}'
    resp = Client().get(f'/atlas/cite/{ref}/')
    assert resp.status_code == 301
    assert resp['Location'] == citations.resolve(ref)['url']


@pytest.mark.django_db
def test_a_permalink_for_nothing_is_a_404():
    assert Client().get('/atlas/cite/persona/nobody/').status_code == 404


@pytest.mark.django_db
def test_an_unknown_format_is_a_404():
    ref = f'persona/{PERSONAS[0]["slug"]}'
    assert Client().get(f'/atlas/cite/{ref}/?format=xml').status_code == 404


@pytest.mark.django_db
def test_bibtex_downloads_as_a_bib_file():
    ref = f'crux/{CRUXES[0]["slug"]}'
    resp = Client().get(f'/atlas/cite/{ref}/?format=bibtex')
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('application/x-bibtex')
    assert '.bib"' in resp['Content-Disposition']
    body = resp.content.decode()
    assert body.startswith('@incollection{atlas-crux-')
    assert CRUXES[0]['title'] in body
    assert 'booktitle  = {Westminster Standards Atlas}' in body


@pytest.mark.django_db
def test_ris_files_the_entry_as_a_reference_work_entry():
    """Zotero maps ENCYC to an encyclopedia article, which is what an Atlas
    page is — filing it as a book chapter would misdescribe it."""
    resp = Client().get(f'/atlas/cite/{POSITION_REF}/?format=ris')
    body = resp.content.decode()
    assert body.startswith('TY  - ENCYC')
    assert 'T2  - Westminster Standards Atlas' in body
    assert body.rstrip().endswith('ER  -')


@pytest.mark.django_db
def test_the_exported_url_is_the_permalink_not_the_page():
    """A footnote should survive the Atlas's routes being reorganised."""
    ref = f'persona/{PERSONAS[0]["slug"]}'
    body = Client().get(f'/atlas/cite/{ref}/?format=bibtex').content.decode()
    assert f'/atlas/cite/{ref}/' in body


@pytest.mark.django_db
def test_the_citation_carries_the_ontology_version():
    DataVersion.objects.update_or_create(
        name=citations.ONTOLOGY_VERSION_KEY, defaults={'data_hash': 'abc123def456789'},
    )
    assert citations.ontology_version() == 'abc123def456'
    body = Client().get(
        f'/atlas/cite/head/{HEADS_OF_DOCTRINE[0]["slug"]}/?format=bibtex'
    ).content.decode()
    assert 'version    = {abc123def456}' in body


@pytest.mark.django_db
def test_an_unloaded_ontology_omits_the_version_rather_than_inventing_one():
    DataVersion.objects.filter(name=citations.ONTOLOGY_VERSION_KEY).delete()
    assert citations.ontology_version() == ''
    body = Client().get(
        f'/atlas/cite/head/{HEADS_OF_DOCTRINE[0]["slug"]}/?format=bibtex'
    ).content.decode()
    assert 'version' not in body


def test_the_plain_citation_reads_as_a_footnote():
    entity = citations.resolve(f'persona/{PERSONAS[0]["slug"]}')
    line = citations.citation_text(entity, url='https://studyreformed.com/x/', version='abc')
    assert line.startswith('Study Reformed, ')
    assert PERSONAS[0]['name'] in line
    assert 'version abc' in line
    assert line.endswith('.')


@pytest.mark.django_db
@pytest.mark.parametrize('kind,ref,title', refs(), ids=lambda v: str(v)[:30])
def test_every_citable_page_offers_the_citation(kind, ref, title):
    entity = citations.resolve(ref)
    body = Client().get(entity['url']).content.decode()
    assert f'Cite this {entity["kind"].lower()}' in body
    assert reverse('westminster_standards:cite', kwargs={'ref': ref}) in body


@pytest.mark.django_db
def test_the_export_records_the_date_it_was_taken():
    resp = Client().get('/atlas/cite/locus/scripture/?format=ris')
    assert f'Y2  - {datetime.date.today():%Y/%m/%d}' in resp.content.decode()
