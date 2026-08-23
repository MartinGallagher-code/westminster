"""Template helpers that make the Atlas's own vocabulary legible.

Two problems these solve. Positions were printed as bare labels —
``Deliberately-Permits-Both`` — with the definition sitting unused in the data
and the page that explains it one unlinked step away. And divines named in
prose were dead ends, though each has a page.
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ..glossary import lookup, url_for
from ..personas import PERSONAS

register = template.Library()


@register.simple_tag
def position(value, dim_key=None, attr_key=None, css_class='ws-position'):
    """Render a position as a link that says what it means.

    Usage: ``{% position row.value_label row.dim_key row.attr.key %}``

    Falls back to plain text when the position cannot be resolved, so a
    template can use this everywhere without checking first.
    """
    entry = lookup(dim_key, attr_key, value)
    if entry is None:
        return escape(value or '')
    definition = entry.get('definition', '')
    title = f' title="{escape(definition)}"' if definition else ''
    return mark_safe(
        f'<a class="{escape(css_class)}" href="{url_for(entry)}"{title}>'
        f'{escape(entry["label"])}</a>'
    )


@register.simple_tag
def position_definition(value, dim_key=None, attr_key=None):
    """The written definition of a position, or an empty string."""
    entry = lookup(dim_key, attr_key, value)
    return entry['definition'] if entry else ''


def _persona_pattern():
    """One alternation over every divine's name, longest first.

    Longest first so "John Arrowsmith of Cambridge" wins over "John
    Arrowsmith"; a single pass so a name inserted into an anchor cannot be
    matched again.
    """
    names = sorted((p['name'] for p in PERSONAS), key=len, reverse=True)
    return re.compile(r'\b(' + '|'.join(re.escape(name) for name in names) + r')\b')


_PERSONA_RE = _persona_pattern()
_PERSONA_URLS = {}


def _persona_url(name):
    if not _PERSONA_URLS:
        from django.urls import reverse
        for persona in PERSONAS:
            _PERSONA_URLS[persona['name']] = (
                persona['slug'],
                reverse('westminster_standards:persona_detail', args=[persona['slug']]),
            )
    return _PERSONA_URLS.get(name)


@register.filter
def link_divines(text, exclude_slug=''):
    """Link every divine named in a passage of prose.

    ``exclude_slug`` keeps a persona's own page from linking to itself, which
    reads as a mistake.

    The text is escaped before any markup is inserted, so prose from the data
    files cannot introduce HTML.
    """
    if not text:
        return ''
    escaped = escape(text)

    def replace(match):
        name = match.group(1)
        found = _persona_url(name)
        if not found:
            return name
        slug, url = found
        if slug == exclude_slug:
            return name
        return f'<a class="ws-link" href="{url}">{name}</a>'

    return mark_safe(_PERSONA_RE.sub(replace, escaped))
