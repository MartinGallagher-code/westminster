"""Links the Atlas renders have to resolve on this site's mount point.

The Atlas is a port of ontologicalatlas.com, which serves it at
``/westminster_standards/``; here it is mounted at ``/atlas/``. Any URL the
ported views build as a literal string therefore 404s, and one did: the home
page's text of the day — the most prominent thing on the page — was a dead
link every day, for every visitor. Nothing caught it, because the sitemap
lists destinations rather than the links pages actually render.
"""

import re

import pytest
from django.test import Client

from westminster_standards.templatetags.atlas_tags import atlas_path

HREF = re.compile(r'href="(/[^"]*)"')


def test_an_upstream_path_is_rewritten_to_this_mount():
    assert atlas_path('/westminster_standards/works/wsc/q/35/') == '/atlas/works/wsc/q/35/'


def test_a_fragment_survives_the_rewrite():
    """The WCF text of the day points at one section of a chapter."""
    assert atlas_path('/westminster_standards/works/wcf/chapter/3/#s4') == \
        '/atlas/works/wcf/chapter/3/#s4'


@pytest.mark.parametrize('url', ['/atlas/cruxes/', '', None, '/compare/westminster/'])
def test_anything_else_is_left_alone(url):
    assert atlas_path(url) == url


@pytest.mark.django_db
def test_the_atlas_home_page_links_nothing_at_the_upstream_mount():
    body = Client().get('/atlas/').content.decode()
    stale = [href for href in HREF.findall(body)
             if href.startswith('/westminster_standards/')]
    assert stale == [], stale


@pytest.mark.django_db
def test_the_daily_text_link_is_a_route_this_site_serves():
    """Whichever text the date-seeded picker chose, its URL has to be one this
    site routes. The page itself 404s here only because the test database
    holds no catechism questions; ``check_site_integrity`` fetches it against
    the loaded corpus, which is where a missing question would be a defect.
    """
    from django.urls import Resolver404, resolve

    from westminster_standards.views import _pick_daily_text

    daily = _pick_daily_text()
    assert daily is not None
    path = atlas_path(daily['url']).split('#')[0]
    try:
        match = resolve(path)
    except Resolver404:                                  # pragma: no cover
        pytest.fail(f'the text of the day links to an unrouted path: {path}')
    assert match.namespace == 'westminster_standards'
