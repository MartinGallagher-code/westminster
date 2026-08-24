"""Icons the site declares have to exist and be served.

The site declared one SVG icon and nothing else. Browsers ask for
/favicon.ico at the root regardless — so every such request 404'd, which a
browser check of /health/ surfaced, that page rendering no <head> to declare
an icon from. There was also no touch icon, so adding the site to a phone's
home screen produced a screenshot rather than an icon: a poor showing for a
site whose memorisation drills are a daily, phone-shaped habit.
"""

import json
import pathlib

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client

DECLARED = [
    'img/favicon.svg',
    'img/favicon-32.png',
    'img/apple-touch-icon.png',
    'img/favicon.ico',
]


@pytest.mark.parametrize('path', DECLARED)
def test_every_declared_asset_is_on_disk(path):
    assert finders.find(path), f'{path} is referenced but not in static files'


@pytest.mark.django_db
def test_the_root_favicon_is_served():
    resp = Client().get('/favicon.ico')
    assert resp.status_code == 301
    assert resp['Location'].endswith('.ico')


@pytest.mark.django_db
def test_a_page_declares_the_touch_icon_and_the_manifest():
    body = Client().get('/').content.decode()
    assert 'rel="apple-touch-icon"' in body
    assert 'rel="manifest"' in body


@pytest.mark.django_db
def test_the_manifest_is_valid_and_its_icons_resolve():
    resp = Client().get('/site.webmanifest')
    assert resp.status_code == 200
    assert resp['Content-Type'].startswith('application/manifest+json')

    manifest = json.loads(resp.content.decode())
    assert manifest['name']
    assert manifest['start_url'] == '/'
    assert manifest['icons']
    for icon in manifest['icons']:
        assert icon['src'].startswith(settings.STATIC_URL), icon
        relative = icon['src'].removeprefix(settings.STATIC_URL)
        assert finders.find(relative), f'{icon["src"]} is in the manifest but missing'


@pytest.mark.django_db
def test_the_manifest_names_the_icons_the_storage_produced():
    """A static JSON file is not post-processed the way CSS is, so its icon
    paths would name unhashed files that are only incidentally still there.
    Rendering it means the URLs come from the same place every other asset's
    do."""
    from django.contrib.staticfiles.storage import staticfiles_storage

    manifest = json.loads(Client().get('/site.webmanifest').content.decode())
    sources = {icon['src'] for icon in manifest['icons']}
    assert staticfiles_storage.url('img/icon-192.png') in sources


def png_size(path):
    """Width and height from the PNG header, so the check needs no imaging
    library: IHDR is always the first chunk, its dimensions two big-endian
    32-bit integers at byte 16."""
    header = pathlib.Path(path).read_bytes()[:24]
    assert header[:8] == b'\x89PNG\r\n\x1a\n', path
    return (
        int.from_bytes(header[16:20], 'big'),
        int.from_bytes(header[20:24], 'big'),
    )


@pytest.mark.parametrize('path,expected', [
    ('img/apple-touch-icon.png', 180),
    ('img/favicon-32.png', 32),
    ('img/icon-192.png', 192),
    ('img/icon-512.png', 512),
])
def test_an_icon_is_the_size_it_claims(path, expected):
    """A phone crops the touch icon to a square at the declared size; a
    mismatch shows as a blurred or letterboxed home-screen icon."""
    assert png_size(finders.find(path)) == (expected, expected)
