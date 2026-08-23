"""The site must not depend on third-party asset hosts.

Bootstrap, its icon font and both typefaces used to load from cdn.jsdelivr.net
and Google Fonts. That made the whole design contingent on two other companies
being reachable — with them blocked the site rendered as unstyled markup — and
disclosed every visitor's IP address to both on every page load. They are now
vendored under ``static/vendor``.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings

# Hosts that must never appear in a stylesheet, script or font reference.
ASSET_HOSTS = (
    'cdn.jsdelivr.net',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'unpkg.com',
    'cdnjs.cloudflare.com',
    'ajax.googleapis.com',
    'use.fontawesome.com',
)

ASSET_ATTRIBUTE_RE = re.compile(
    r'(?:src|href)\s*=\s*["\'](https?:)?//([^"\'/]+)', re.IGNORECASE,
)


def _templates():
    for directory in settings.TEMPLATES[0]['DIRS']:
        yield from Path(directory).rglob('*.html')


def test_no_template_loads_an_asset_from_a_third_party_host():
    offenders = []
    for template in _templates():
        text = template.read_text()
        for host in ASSET_HOSTS:
            if host in text:
                offenders.append(f'{template.relative_to(settings.BASE_DIR)} → {host}')
    assert offenders == [], (
        'Vendor these under static/vendor/ instead: ' + '; '.join(offenders)
    )


def test_vendored_assets_are_present():
    vendor = Path(settings.BASE_DIR) / 'static' / 'vendor'
    for relative in (
        'bootstrap/bootstrap.min.css',
        'bootstrap/bootstrap.bundle.min.js',
        'bootstrap-icons/bootstrap-icons.min.css',
        'bootstrap-icons/fonts/bootstrap-icons.woff2',
        'fonts/fonts.css',
    ):
        assert (vendor / relative).is_file(), f'missing vendored asset: {relative}'


def test_every_font_the_stylesheet_references_exists():
    """A dangling url() breaks `collectstatic` on deploy, not in development."""
    fonts = Path(settings.BASE_DIR) / 'static' / 'vendor' / 'fonts'
    css = (fonts / 'fonts.css').read_text()
    referenced = set(re.findall(r"url\(['\"]?\./([^'\")]+)", css))
    assert referenced, 'fonts.css references no font files'
    missing = sorted(name for name in referenced if not (fonts / name).is_file())
    assert missing == [], f'fonts.css references missing files: {missing}'


def test_the_icon_stylesheet_points_at_the_vendored_font_files():
    icons = Path(settings.BASE_DIR) / 'static' / 'vendor' / 'bootstrap-icons'
    css = (icons / 'bootstrap-icons.min.css').read_text()
    referenced = {
        name.split('?')[0]
        for name in re.findall(r"url\(['\"]?([^'\")]+)", css)
        if not name.startswith('data:')
    }
    assert referenced
    missing = sorted(name for name in referenced if not (icons / name).is_file())
    assert missing == [], f'icon CSS references missing files: {missing}'


def test_vendored_css_has_no_source_map_reference():
    """Django's manifest storage resolves sourceMappingURL and fails when the
    .map is absent, which would break the deploy rather than a test."""
    bootstrap = Path(settings.BASE_DIR) / 'static' / 'vendor' / 'bootstrap'
    for name in ('bootstrap.min.css', 'bootstrap.bundle.min.js'):
        assert 'sourceMappingURL' not in (bootstrap / name).read_text()


@pytest.mark.parametrize('directory,licence', [
    ('bootstrap', 'LICENSE'),
    ('bootstrap-icons', 'LICENSE'),
    ('fonts', 'OFL.txt'),
])
def test_vendored_code_keeps_its_licence(directory, licence):
    path = Path(settings.BASE_DIR) / 'static' / 'vendor' / directory / licence
    assert path.is_file(), f'missing licence for vendored {directory}'
    assert path.read_text().strip()
