"""Search over the layers the Atlas uniquely owns, for reuse across the site.

Study Reformed's own search covers the *text* of the Standards (every
Confession section and catechism question, with commentary and proof texts),
so a site-wide search only needs the Atlas for what has no counterpart there:
its personas, cruxes, schools, and heads of doctrine. Keeping that matching
here — rather than in ``views.py`` — leaves the ported view module untouched
for future syncs with the upstream ontologicalatlas.com app, while giving the
site search a single call to make.

The Atlas's own ``/atlas/search/`` page remains the richer search: it also
matches the full text of the works the Atlas hosts.
"""

from urllib.parse import urlencode

from django.urls import reverse

from .cruxes import CRUXES
from .heads_of_doctrine import HEADS_OF_DOCTRINE
from .personas import PERSONAS
from .schools import SCHOOLS

MIN_QUERY_LENGTH = 2


def _matches(needle, *haystacks):
    return any(needle in (h or '').lower() for h in haystacks)


def _group(label, icon, items, query, limit):
    """Trim a layer's matches to ``limit`` and record how many were found."""
    if not items:
        return None
    return {
        'label': label,
        'icon': icon,
        'items': items[:limit],
        'total': len(items),
        'has_more': len(items) > limit,
        'more_url': (
            reverse('westminster_standards:search') + '?' + urlencode({'q': query})
        ),
    }


def search_entities(query, limit=5):
    """Matching Atlas personas, cruxes, schools, and heads, grouped by layer.

    Returns a list of groups in a fixed order, each with at most ``limit``
    items; layers with no matches are omitted. An empty or too-short query
    returns an empty list.
    """
    query = (query or '').strip()
    if len(query) < MIN_QUERY_LENGTH:
        return []
    needle = query.lower()

    heads = [
        {
            'name': h['name'],
            'description': h.get('description', ''),
            'url': reverse('westminster_standards:head_detail', args=[h['slug']]),
        }
        for h in HEADS_OF_DOCTRINE
        if _matches(needle, h['name'], h.get('description'))
    ]
    personas = [
        {
            'name': p['name'],
            'description': p.get('tagline') or p.get('role') or p.get('bio', ''),
            'meta': p.get('dates', ''),
            'url': reverse('westminster_standards:persona_detail', args=[p['slug']]),
        }
        for p in PERSONAS
        if _matches(needle, p['name'], p.get('bio'), p.get('tagline'), p.get('role'))
    ]
    cruxes = [
        {
            'name': c['title'],
            'description': c.get('tagline') or c.get('summary', ''),
            'url': reverse('westminster_standards:crux_detail', args=[c['slug']]),
        }
        for c in CRUXES
        if _matches(needle, c['title'], c.get('tagline'), c.get('summary'),
                    c.get('background'), c.get('language'))
    ]
    schools = [
        {
            'name': s['name'],
            'description': s.get('description', ''),
            'url': reverse('westminster_standards:school_detail', args=[s['slug']]),
        }
        for s in SCHOOLS
        if _matches(needle, s['name'], s.get('description'), s.get('origin'))
    ]

    groups = [
        _group('Heads of doctrine', 'bi-diagram-2', heads, query, limit),
        _group('Cruxes', 'bi-lightning', cruxes, query, limit),
        _group('Divines', 'bi-people', personas, query, limit),
        _group('Schools & traditions', 'bi-bank', schools, query, limit),
    ]
    return [g for g in groups if g]
