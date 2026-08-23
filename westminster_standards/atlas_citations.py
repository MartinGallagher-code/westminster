"""Make the Atlas's own scholarship citable.

Study Reformed already exports citations for the *texts* it hosts — WCF 3.4
resolves to a permalink, a BibTeX entry and an RIS record. The Atlas is a
different kind of source: not a historic document but a reference work with
its own claims, and a seminarian who wants to cite "Hypothetical-Universal" as
the Atlas defines it, or its reading of the Sabbath crux, had nothing to put
in a footnote.

Every citable Atlas page therefore has a reference of the form
``persona/john-arrowsmith`` or ``position/soteriology/atonement-extent/
hypothetical-universal``, which is stable across redesigns, and a version
stamp taken from the hash of the ontology data itself — so a citation names
the state of the Atlas it was read in, not just its address.

Kept out of ``views.py`` so the ported module stays syncable with upstream.
"""

from datetime import date

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from .cruxes import CRUXES
from .data import DIMENSIONS, DIMENSION_PAIRS
from .glossary import VALUE_BY_KEYS
from .heads_of_doctrine import HEADS_OF_DOCTRINE
from .personas import PERSONAS
from .schools import SCHOOLS

ATLAS_TITLE = 'Westminster Standards Atlas'
ATLAS_AUTHOR = 'Study Reformed'
ONTOLOGY_VERSION_KEY = 'westminster-ontology'

FORMATS = ('bibtex', 'ris')


def ontology_version():
    """A short stamp for the ontology the reader is citing.

    The loader already records a SHA-256 of the ontology source; the first
    twelve characters are enough to tell two states of the Atlas apart, and
    short enough to sit in a footnote. Returns '' when the data has never been
    loaded, in which case the citation simply omits the version rather than
    claiming one.
    """
    from catechism.models import DataVersion

    row = DataVersion.objects.filter(name=ONTOLOGY_VERSION_KEY).first()
    return row.data_hash[:12] if row and row.data_hash else ''


def _entry(kind, ref, title, url, part=None):
    return {'kind': kind, 'ref': ref, 'title': title, 'url': url, 'part': part}


def _by_slug(collection, slug):
    return next((item for item in collection if item['slug'] == slug), None)


def _persona(parts):
    persona = _by_slug(PERSONAS, parts[0]) if len(parts) == 1 else None
    if persona is None:
        return None
    return _entry(
        'Divine', f'persona/{persona["slug"]}', persona['name'],
        reverse('westminster_standards:persona_detail', args=[persona['slug']]),
        part=persona.get('dates') or None,
    )


def _crux(parts):
    crux = _by_slug(CRUXES, parts[0]) if len(parts) == 1 else None
    if crux is None:
        return None
    return _entry(
        'Crux', f'crux/{crux["slug"]}', crux['title'],
        reverse('westminster_standards:crux_detail', args=[crux['slug']]),
        part=crux.get('dates') or None,
    )


def _head(parts):
    head = _by_slug(HEADS_OF_DOCTRINE, parts[0]) if len(parts) == 1 else None
    if head is None:
        return None
    return _entry(
        'Head of doctrine', f'head/{head["slug"]}', head['name'],
        reverse('westminster_standards:head_detail', args=[head['slug']]),
    )


def _school(parts):
    school = _by_slug(SCHOOLS, parts[0]) if len(parts) == 1 else None
    if school is None:
        return None
    return _entry(
        'School', f'school/{school["slug"]}', school['name'],
        reverse('westminster_standards:school_detail', args=[school['slug']]),
        part=school.get('period') or None,
    )


def _locus(parts):
    if len(parts) != 1:
        return None
    dimension = next((d for d in DIMENSIONS if d['key'] == parts[0]), None)
    if dimension is None:
        return None
    return _entry(
        'Locus', f'locus/{dimension["key"]}', dimension['label'],
        reverse('westminster_standards:dimension_detail', args=[dimension['key']]),
    )


def _position(parts):
    if len(parts) != 3:
        return None
    entry = VALUE_BY_KEYS.get(tuple(parts))
    if entry is None:
        return None
    return _entry(
        'Position',
        'position/{dim_key}/{attr_key}/{value_key}'.format(**entry),
        entry['label'],
        reverse('westminster_standards:value_detail', args=[
            entry['dim_key'], entry['attr_key'], entry['value_key'],
        ]),
        part=f"{entry['dim_label']} — {entry['attr_label']}",
    )


def _pair(parts):
    if len(parts) != 1:
        return None
    pair = next(
        (p for p in DIMENSION_PAIRS if '-'.join(p) == parts[0]), None
    )
    if pair is None:
        return None
    labels = {d['key']: d['label'] for d in DIMENSIONS}
    title = ' × '.join(labels.get(key, key) for key in pair)
    return _entry(
        'Intersection', f'pair/{parts[0]}', title,
        reverse('westminster_standards:dimension_pair_detail', args=[parts[0]]),
    )


RESOLVERS = {
    'persona': _persona,
    'crux': _crux,
    'head': _head,
    'school': _school,
    'locus': _locus,
    'position': _position,
    'pair': _pair,
}


def resolve(ref):
    """Turn a citation reference into the thing it names, or None.

    Deliberately strict: an unknown kind, a wrong number of parts, or a slug
    the ontology does not hold returns None rather than a citation of nothing.
    """
    parts = [part for part in (ref or '').strip('/').split('/') if part]
    if len(parts) < 2:
        return None
    resolver = RESOLVERS.get(parts[0])
    return resolver(parts[1:]) if resolver else None


def citation_key(entity):
    """A BibTeX-safe key, e.g. 'atlas-persona-john-arrowsmith'."""
    return 'atlas-' + entity['ref'].replace('/', '-')


def citation_label(entity):
    """How the reference reads in prose."""
    return f"{ATLAS_TITLE}, “{entity['title']}”"


def citation_text(entity, url='', version=''):
    """A plain citation line for pasting into prose or a footnote."""
    pieces = [f'{ATLAS_AUTHOR}, “{entity["title"]}” ({entity["kind"]})']
    pieces.append(ATLAS_TITLE)
    if version:
        pieces.append(f'version {version}')
    if url:
        pieces.append(url)
    return ', '.join(pieces) + '.'


def bibtex(entity, url='', version='', accessed=None):
    """A BibTeX ``@incollection`` entry for an Atlas page."""
    fields = [
        ('author', ATLAS_AUTHOR),
        ('title', entity['title']),
        ('booktitle', ATLAS_TITLE),
        ('type', entity['kind']),
    ]
    if entity['part']:
        fields.append(('note', entity['part']))
    if version:
        fields.append(('version', version))
    if url:
        fields.append(('url', url))
    if accessed:
        fields.append(('urldate', f'{accessed:%Y-%m-%d}'))

    body = ',\n'.join(f'  {name:<10} = {{{value}}}' for name, value in fields)
    return f'@incollection{{{citation_key(entity)},\n{body}\n}}\n'


def ris(entity, url='', version='', accessed=None):
    """An RIS record — the format Zotero, EndNote and Mendeley import.

    ``ENCYC`` rather than ``CHAP``: an Atlas page is an entry in a reference
    work, and that is how the managers will file it.
    """
    lines = [
        'TY  - ENCYC',
        f'AU  - {ATLAS_AUTHOR}',
        f'TI  - {entity["title"]}',
        f'T2  - {ATLAS_TITLE}',
    ]
    if version:
        lines.append(f'ET  - {version}')
    if url:
        lines.append(f'UR  - {url}')
    if accessed:
        lines.append(f'Y2  - {accessed:%Y/%m/%d}')
    note = ' — '.join(filter(None, [entity['kind'], entity['part']]))
    lines += [f'N1  - {note}', 'ER  - ']
    return '\n'.join(lines) + '\n'


EXPORTERS = {
    'bibtex': (bibtex, 'application/x-bibtex', 'bib'),
    'ris': (ris, 'application/x-research-info-systems', 'ris'),
}


def cite(request, ref):
    """``/atlas/cite/<ref>/`` — the stable address of an Atlas page.

    Plain, it redirects to the page, so a footnote's URL survives a redesign
    of the Atlas's routes. With ``?format=bibtex`` or ``?format=ris`` it hands
    back the record a reference manager imports.
    """
    entity = resolve(ref)
    if entity is None:
        raise Http404(f'Nothing in the Atlas is cited as {ref!r}')

    fmt = request.GET.get('format')
    if not fmt:
        return redirect(entity['url'], permanent=True)
    if fmt not in EXPORTERS:
        raise Http404(f'Unknown citation format {fmt!r}')

    render_citation, content_type, extension = EXPORTERS[fmt]
    permalink = request.build_absolute_uri(
        reverse('westminster_standards:cite', kwargs={'ref': entity['ref']})
    )
    body = render_citation(
        entity, url=permalink, version=ontology_version(), accessed=date.today(),
    )
    response = HttpResponse(body, content_type=f'{content_type}; charset=utf-8')
    filename = f'{citation_key(entity)}.{extension}'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
