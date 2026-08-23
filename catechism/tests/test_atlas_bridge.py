"""Integration between the Westminster Standards Atlas and Study Reformed:

Phase 3 — on-page Atlas links resolve internally, and the Atlas's duplicate
Confession/catechism full-text pages redirect to Study Reformed.
Phase 4 — the comparison-theme taxonomy crosswalks to Atlas loci, and
Confession chapters / catechism topics show the Atlas loci they treat.
Phase 5 — the Atlas owns the single doctrine-head taxonomy, the loci panel is
driven by the loaded ontology, and site search reaches the Atlas layers.
"""

import pytest
from django.core.management import call_command

from catechism.atlas import atlas_url, comparison_locus_atlas, topic_loci
from catechism.models import DoctrineHead, Question, Topic
from westminster_standards.entity_search import search_entities
from westminster_standards.sitemap import atlas_sitemap_paths
from .conftest import (
    OntologyAttributeFactory, OntologyLocusFactory, QuestionFactory,
    QuestionOntologyTagFactory,
)


def test_atlas_url_defaults_to_internal_mount():
    # No WESTMINSTER_ATLAS_BASE_URL override: links stay on-site under /atlas/.
    assert atlas_url() == '/atlas/'
    assert atlas_url('/westminster_standards/dimension/scripture/') == '/atlas/dimension/scripture/'
    assert atlas_url('heads/prolegomena/') == '/atlas/heads/prolegomena/'


@pytest.mark.django_db
def test_catechism_question_page_redirects_to_study_reformed(client, question):
    resp = client.get('/atlas/works/wsc/q/1/')
    assert resp.status_code == 302
    assert resp['Location'] == question.get_absolute_url() == '/wsc/questions/1/'


@pytest.mark.django_db
def test_missing_catechism_question_is_404(client, catechism):
    assert client.get('/atlas/works/wsc/q/999/').status_code == 404


@pytest.mark.django_db
def test_wcf_chapter_page_redirects_to_study_reformed(client, confession):
    chapter = Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1,
        question_start=1, question_end=10,
    )
    resp = client.get('/atlas/works/wcf/chapter/1/')
    assert resp.status_code == 302
    assert resp['Location'] == chapter.get_absolute_url() == '/wcf/chapters/of-the-holy-scripture/'


@pytest.mark.django_db
def test_work_detail_redirects_hosted_standards_but_keeps_service_books(client, catechism):
    # WSC is hosted by Study Reformed -> redirect to its document home.
    resp = client.get('/atlas/works/wsc/')
    assert resp.status_code == 302
    assert resp['Location'] == '/wsc/'
    # The Directory for Public Worship has no Study Reformed page -> Atlas keeps it.
    assert client.get('/atlas/works/dpw/').status_code == 200


# --- Phase 4: taxonomy crosswalk + chapter/topic reverse links -------------

def test_comparison_locus_crosswalk_resolves_and_ignores_unknown():
    assert comparison_locus_atlas('Soteriology') == {
        'key': 'soteriology', 'label': 'Soteriology',
        'url': '/atlas/dimension/soteriology/',
    }
    # Case/whitespace tolerant.
    assert comparison_locus_atlas('  prolegomena ')['key'] == 'scripture'
    # Unknown / blank -> no link.
    assert comparison_locus_atlas('Angelology') is None
    assert comparison_locus_atlas('') is None


@pytest.mark.django_db
def test_topic_loci_for_wcf_chapter(confession):
    chapter = Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1,
        question_start=1, question_end=10,
    )
    loci = topic_loci(chapter)
    keys = [locus['key'] for locus in loci]
    assert 'scripture' in keys
    for locus in loci:
        assert locus['url'].startswith('/atlas/dimension/')
        assert locus['label'] and locus['color']


@pytest.mark.django_db
def test_topic_loci_for_catechism_topic(catechism, topic, question):
    loci = topic_loci(topic)          # WSC topic covering question 1
    assert [locus['key'] for locus in loci]  # non-empty
    assert all(locus['url'].startswith('/atlas/dimension/') for locus in loci)


@pytest.mark.django_db
def test_topic_loci_empty_for_non_westminster_document(db):
    from catechism.tests.conftest import CatechismFactory  # noqa
    from catechism.models import Catechism
    heidelberg = Catechism.objects.create(
        name='Heidelberg Catechism', abbreviation='HC', slug='heidelberg',
        total_questions=1, document_type=Catechism.CATECHISM,
    )
    t = Topic.objects.create(
        catechism=heidelberg, name='Comfort', slug='comfort', order=1,
        question_start=1, question_end=1,
    )
    assert topic_loci(t) == []


@pytest.mark.django_db
def test_confession_chapter_page_renders_atlas_loci_panel(client, confession):
    Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1,
        question_start=1, question_end=10,
    )
    resp = client.get('/wcf/chapters/of-the-holy-scripture/')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert 'Loci treated here' in body
    assert '/atlas/dimension/scripture/' in body


# --- Phase 5: one head taxonomy, ontology-driven loci, site-wide search -----


@pytest.mark.django_db
def test_doctrine_heads_mirror_the_atlas_taxonomy():
    """The Atlas app owns the head taxonomy; the database mirrors it.

    Regression: the database carried its own 33 heads whose slugs mostly did
    not exist in the Atlas, so their chips linked to Atlas pages that 404'd.
    """
    from westminster_standards.heads_of_doctrine import HEADS_OF_DOCTRINE

    call_command('load_catechism')
    call_command('load_westminster_ontology')

    assert set(DoctrineHead.objects.values_list('slug', flat=True)) == {
        head['slug'] for head in HEADS_OF_DOCTRINE
    }


@pytest.mark.django_db
def test_every_doctrine_head_chip_links_to_a_real_atlas_page(client):
    call_command('load_catechism')
    call_command('load_westminster_ontology')

    broken = [
        head.slug for head in DoctrineHead.objects.all()
        if client.get(head.get_atlas_url()).status_code != 200
    ]
    assert broken == []


@pytest.mark.django_db
def test_every_catechism_question_is_linked_to_a_doctrine_head():
    call_command('load_catechism')
    call_command('load_westminster_ontology')

    unlinked = [
        question.number
        for question in Question.objects.filter(catechism__slug='wsc')
        if not question.doctrine_head_links.exists()
    ]
    assert unlinked == []


@pytest.mark.django_db
def test_topic_loci_prefers_the_loaded_ontology_over_the_static_mapping(confession):
    """A tagged chapter reports the loci the ontology gives it, not the fallback."""
    chapter = Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1,
        question_start=1, question_end=1,
    )
    question = QuestionFactory(
        catechism=confession, topic=chapter, number=1,
    )
    # Chapter 1 maps to 'scripture' in the Atlas's static mapping; tag it with
    # an attribute from a different locus and the loaded ontology must win.
    locus = OntologyLocusFactory(slug='soteriology', name='Soteriology', order=5)
    attribute = OntologyAttributeFactory(locus=locus, slug='justification', name='Justification')
    QuestionOntologyTagFactory(question=question, attribute=attribute)

    keys = [entry['key'] for entry in topic_loci(chapter)]
    assert keys == ['soteriology']


@pytest.mark.django_db
def test_topic_loci_falls_back_when_the_ontology_is_not_loaded(confession):
    """A database with the texts but no ontology still renders the panel."""
    chapter = Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture',
        slug='of-the-holy-scripture', order=1,
        question_start=1, question_end=10,
    )
    assert [entry['key'] for entry in topic_loci(chapter)] == ['scripture']


def test_search_entities_groups_matches_and_respects_the_limit():
    groups = search_entities('covenant', limit=2)
    labels = [group['label'] for group in groups]
    assert 'Heads of doctrine' in labels and 'Divines' in labels
    for group in groups:
        assert len(group['items']) <= 2
        assert group['total'] >= len(group['items'])
        assert group['more_url'].startswith('/atlas/search/?q=')
        for item in group['items']:
            assert item['name'] and item['url'].startswith('/atlas/')


def test_search_entities_ignores_blank_and_too_short_queries():
    assert search_entities('') == []
    assert search_entities('a') == []
    assert search_entities('xyzzy') == []


@pytest.mark.django_db
def test_site_search_surfaces_atlas_results(client):
    resp = client.get('/search/?q=Rutherford')
    assert resp.status_code == 200
    assert resp.context['atlas_total'] > 0
    body = resp.content.decode()
    assert 'Also in the Atlas' in body
    assert '/atlas/personas/samuel-rutherford/' in body


@pytest.mark.django_db
def test_site_search_reports_atlas_matches_when_the_standards_have_none(client):
    resp = client.get('/search/?q=Rutherford')
    assert resp.context['grouped_results'] == []
    assert 'result' in resp.content.decode()
    assert 'in the Atlas for' in resp.content.decode()


# --- Phase 6: the Atlas is in the sitemap ----------------------------------


@pytest.mark.django_db
def test_sitemap_includes_the_atlas(client):
    body = client.get('/sitemap.xml').content.decode()
    assert '/atlas/ontology/' in body
    assert '/atlas/personas/samuel-rutherford/' in body
    assert '/atlas/heads/justification/' in body


def test_atlas_sitemap_excludes_routes_that_redirect():
    """A sitemap advertises destinations, not redirects.

    The Atlas's pages for the three Standards Study Reformed hosts redirect to
    its canonical pages (bridge.py), so they must not be listed.
    """
    paths = set(atlas_sitemap_paths())
    assert '/atlas/works/dpw/' in paths          # the Atlas hosts this one
    assert '/atlas/works/wcf/' not in paths
    assert '/atlas/works/wsc/' not in paths
    assert '/atlas/works/wlc/' not in paths


@pytest.mark.django_db
def test_every_atlas_sitemap_url_resolves(client):
    paths = atlas_sitemap_paths()
    assert len(paths) == len(set(paths)), 'sitemap paths must be unique'
    # Spot-check one page per layer; the full sweep of all 432 is too slow for
    # the unit suite and is covered by the loaded-data integrity check.
    sample = [
        '/atlas/', '/atlas/ontology/', '/atlas/dimension/scripture/',
        '/atlas/dimension/scripture/canon/sixty_six/',
        '/atlas/heads/justification/', '/atlas/cruxes/the-order-of-the-decrees/',
        '/atlas/personas/samuel-rutherford/', '/atlas/works/ssk/',
    ]
    for path in sample:
        assert path in paths, path
        assert client.get(path).status_code == 200, path
