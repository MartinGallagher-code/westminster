"""Django strips ``{# ... #}`` only when it opens and closes on one line.

A multi-line one is not a comment at all: the template renders the comment
text, braces and all, into the page. It has happened twice — once on the
comparison pages, once on the parallel reading — and neither time did a test
that rendered some other page catch it. This one reads the templates instead,
so a new page cannot reintroduce it.
"""

import pathlib

import pytest
from django.conf import settings
from django.template.utils import get_app_template_dirs

# Both halves of the search path: the project's own templates/ and every
# app's templates/ directory. The Atlas keeps its pages in the latter.
TEMPLATE_ROOTS = [
    pathlib.Path(directory)
    for engine in settings.TEMPLATES
    for directory in engine.get('DIRS', [])
] + [pathlib.Path(directory) for directory in get_app_template_dirs('templates')]


def template_files():
    seen = set()
    for root in TEMPLATE_ROOTS:
        for path in sorted(root.rglob('*.html')):
            if path not in seen:
                seen.add(path)
                yield path


def test_there_are_templates_to_check():
    """A check that silently examines nothing is not a check."""
    assert len(list(template_files())) > 50


@pytest.mark.parametrize('path', list(template_files()), ids=lambda p: p.name)
def test_no_comment_is_left_open_at_the_end_of_a_line(path):
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if '{#' in line and '#}' not in line.split('{#', 1)[1]:
            pytest.fail(
                f'{path}:{number} opens {{# without closing it on the same '
                f'line, so Django will render it verbatim. Use '
                f'{{% comment %}}...{{% endcomment %}} instead.\n  {line.strip()}'
            )
