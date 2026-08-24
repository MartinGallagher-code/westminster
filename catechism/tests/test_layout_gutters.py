"""A wide-gutter row has to sit in a container wide enough to hold it.

Bootstrap pairs a container's 0.75rem side padding with a row's default 1.5rem
gutter and cancels the row's negative margins against it. A row asking for a
wider gutter — ``g-5`` is 3rem — pulls 0.75rem past the container on each side,
and the page scrolls sideways at every width. Eight pages did: every document
home, the Scripture index and book pages, both learn pages, and both auth
pages. No test could see it, because the markup is valid and the pages render.

This reads the templates instead. A page that opts into a wide gutter must
also say where the room comes from.
"""

import pathlib
import re

import pytest
from django.conf import settings
from django.template.utils import get_app_template_dirs

WIDE_GUTTER = re.compile(r'class="row\b[^"]*\bg[xy]?-5\b')

# Either the page widens the main container, or the row sits inside a band
# that already carries the wider inset.
ROOM_FOR_THE_GUTTER = ('gutter-wide', 'page-band-content')

TEMPLATE_ROOTS = [
    pathlib.Path(directory)
    for engine in settings.TEMPLATES
    for directory in engine.get('DIRS', [])
] + [pathlib.Path(directory) for directory in get_app_template_dirs('templates')]


def templates_with_a_wide_gutter_row():
    found = []
    for root in TEMPLATE_ROOTS:
        for path in sorted(root.rglob('*.html')):
            if WIDE_GUTTER.search(path.read_text()):
                found.append(path)
    return found


def test_the_check_has_something_to_check():
    assert templates_with_a_wide_gutter_row()


@pytest.mark.parametrize(
    'path', templates_with_a_wide_gutter_row(), ids=lambda p: p.name,
)
def test_a_wide_gutter_row_has_room_for_its_gutter(path):
    text = path.read_text()
    assert any(marker in text for marker in ROOM_FOR_THE_GUTTER), (
        f'{path} uses a g-5 row but neither widens the main container '
        f'(main_wrapper_class "... gutter-wide") nor puts the row inside a '
        f'.page-band-content. As written the page scrolls sideways by 12px.'
    )


def test_the_widening_class_is_defined():
    """The templates name a class; something has to define it."""
    css = (pathlib.Path(settings.BASE_DIR) / 'static' / 'css' / 'styles.css').read_text()
    assert '.gutter-wide {' in css
