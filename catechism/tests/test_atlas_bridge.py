"""Phase 3 integration: on-page Atlas links resolve internally, and the Atlas's
duplicate Confession/catechism full-text pages redirect to Study Reformed."""

import pytest

from catechism.atlas import atlas_url
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
