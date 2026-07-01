from urllib.parse import urljoin

from django.conf import settings


# The Westminster Standards Atlas now lives natively in this project, mounted
# at /atlas/ (see config/urls.py and the westminster_standards app), so links
# resolve internally by default. Set WESTMINSTER_ATLAS_BASE_URL to point back
# at the public ontologicalatlas.com deployment if that is ever wanted.
DEFAULT_ATLAS_BASE_URL = '/atlas/'


def atlas_base_url():
    return getattr(settings, 'WESTMINSTER_ATLAS_BASE_URL', DEFAULT_ATLAS_BASE_URL).rstrip('/') + '/'


def atlas_url(path=''):
    clean_path = path.lstrip('/')
    legacy_prefix = 'westminster_standards/'
    if clean_path.startswith(legacy_prefix):
        clean_path = clean_path[len(legacy_prefix):]
    return urljoin(atlas_base_url(), clean_path)


def dimension_url(locus_key):
    """Internal URL for an Atlas locus (dimension) page."""
    return atlas_url(f'dimension/{locus_key}/')


# --- Taxonomy crosswalk (Phase 4) -----------------------------------------
#
# The hand-authored comparison themes are tagged with a classical
# systematic-theology locus (a free-text string). The Atlas ontology instead
# organises the same ground into the eight Westminster loci. This crosswalk
# maps each comparison locus onto its nearest Atlas locus so the two
# taxonomies cross-link. It is a *nearest-fit* guide: a few classical loci
# (e.g. Hamartiology, "Christian Life and Liberty") straddle more than one
# Atlas locus, and are mapped to the closest single one.
COMPARISON_LOCUS_TO_ONTOLOGY = {
    'prolegomena': 'scripture',
    'theology proper': 'god_decree',
    'creation and providence': 'god_decree',
    'hamartiology': 'covenant',
    'christology': 'christology',
    'christology and covenant': 'covenant',
    'soteriology': 'soteriology',
    'the law of god': 'law_sanctification',
    'christian life': 'law_sanctification',
    'christian life and liberty': 'law_sanctification',
    'ecclesiology': 'ecclesiology_worship',
    'eschatology': 'civil_last_things',
}


# The eight locus accent colours (mirrors the Atlas palette in
# westminster_standards/templates/.../base.html). Used to tint cross-link
# chips on Study Reformed pages, which do not load the Atlas CSS variables.
LOCUS_COLORS = {
    'scripture': '#fcd34d',
    'god_decree': '#c084fc',
    'covenant': '#60a5fa',
    'christology': '#f87171',
    'soteriology': '#34d399',
    'law_sanctification': '#fb923c',
    'ecclesiology_worship': '#f472b6',
    'civil_last_things': '#38bdf8',
}


def _dimension_labels():
    """Map of Atlas locus key -> display label, read from the ontology data."""
    from westminster_standards.data import DIMENSIONS
    return {d['key']: d['label'] for d in DIMENSIONS}


def comparison_locus_atlas(locus_text):
    """Resolve a comparison theme's free-text locus to its Atlas locus.

    Returns a dict ``{'key', 'label', 'url'}`` for the nearest Atlas locus, or
    ``None`` when the locus is blank or unrecognised.
    """
    if not locus_text:
        return None
    key = COMPARISON_LOCUS_TO_ONTOLOGY.get(locus_text.strip().lower())
    if not key:
        return None
    label = _dimension_labels().get(key, locus_text)
    return {'key': key, 'label': label, 'url': dimension_url(key)}


def topic_loci(topic):
    """The Atlas loci a Westminster chapter/topic bears on, for reverse links.

    Uses the Atlas's comprehensive chapter/question -> locus mapping (which
    covers every Confession chapter and catechism question), so the panel is
    populated even though the per-question ontology tags in the database are
    still sparse. Returns an ordered list of ``{'key','label','icon','tagline','url'}``
    in canonical locus order; empty for non-Westminster documents.
    """
    slug = topic.catechism.slug
    from westminster_standards.data import DIMENSIONS
    from westminster_standards.locus_mapping import (
        wcf_chapter_loci, catechism_question_loci,
    )

    keys = set()
    if slug == 'wcf':
        keys.update(wcf_chapter_loci(topic.order))
    elif slug in ('wsc', 'wlc'):
        for question in topic.questions.all():
            keys.update(catechism_question_loci(slug, question.number))
    else:
        return []

    payload = []
    for d in DIMENSIONS:                     # canonical locus order
        if d['key'] in keys:
            payload.append({
                'key': d['key'],
                'label': d['label'],
                'icon': d['icon'],
                'tagline': d['tagline'],
                'color': LOCUS_COLORS.get(d['key'], ''),
                'url': dimension_url(d['key']),
            })
    return payload
