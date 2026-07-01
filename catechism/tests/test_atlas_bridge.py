"""Integration between the Westminster Standards Atlas and Study Reformed:

Phase 3 — on-page Atlas links resolve internally, and the Atlas's duplicate
Confession/catechism full-text pages redirect to Study Reformed.
Phase 4 — the comparison-theme taxonomy crosswalks to Atlas loci, and
Confession chapters / catechism topics show the Atlas loci they treat.
"""

import pytest

from catechism.atlas import atlas_url, comparison_locus_atlas, topic_loci
from catechism.models import Topic


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


# --- Doctrine-head links resolve (specific page when it exists, else locus) --

@pytest.mark.django_db
def test_doctrine_head_link_falls_back_to_locus_when_no_atlas_head_page(client):
    from catechism.models import OntologyLocus, DoctrineHead
    locus = OntologyLocus.objects.create(slug='god_decree', name='God & Decree', order=2)
    # The Confession-chapter head 'eternal_decree' has no Atlas head page
    # (the Atlas uses 'the-eternal-decree'), so the chip must not 404.
    head = DoctrineHead.objects.create(
        slug='eternal_decree', name="Of God's Eternal Decree", locus=locus,
        atlas_path='/westminster_standards/heads/eternal_decree/',
    )
    url = head.get_atlas_url()
    assert url == '/atlas/dimension/god_decree/'
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_doctrine_head_link_uses_specific_page_when_it_exists(client):
    from catechism.models import OntologyLocus, DoctrineHead
    locus = OntologyLocus.objects.create(slug='soteriology', name='Soteriology', order=5)
    head = DoctrineHead.objects.create(
        slug='justification', name='Of Justification', locus=locus,
        atlas_path='/westminster_standards/heads/justification/',
    )
    url = head.get_atlas_url()
    assert url == '/atlas/heads/justification/'
    assert client.get(url).status_code == 200
