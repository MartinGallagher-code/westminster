"""Parse Westminster citations in free-text strings and resolve them to URLs.

Used to:

  1. Linkify the cruxes' `language` and `references` fields so a quoted
     "WCF III.7" or "Larger Catechism Q. 50" becomes a hyperlink to the
     loaded chapter/question text.
  2. Build a reverse index — for each WCF chapter and each catechism
     question, list the cruxes that reference it — so the chapter and
     question pages can show "cruxes that bear on this text."

The supported citation patterns are conservative; the goal is high
precision (no spurious links) rather than high recall (occasional
unlinked references are acceptable).

Recognised forms:

  - WCF + Roman numeral 1-33, optionally followed by .section[, section]
    e.g.  "WCF I.6"  "WCF III.7"  "WCF XXII.1-7"  "WCF VIII.5, 8"
  - Larger Catechism Q. N  /  LC Q. N
  - Shorter Catechism Q. N  /  SC Q. N

Catechism question ranges are also matched (e.g. "LC Q. 91-148"); the
first number is treated as the canonical target.
"""

import re

from django.urls import reverse
from django.utils.html import escape, mark_safe


ROMAN_TO_INT = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
    'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13,
    'XIV': 14, 'XV': 15, 'XVI': 16, 'XVII': 17, 'XVIII': 18,
    'XIX': 19, 'XX': 20, 'XXI': 21, 'XXII': 22, 'XXIII': 23,
    'XXIV': 24, 'XXV': 25, 'XXVI': 26, 'XXVII': 27, 'XXVIII': 28,
    'XXIX': 29, 'XXX': 30, 'XXXI': 31, 'XXXII': 32, 'XXXIII': 33,
}

# Build the WCF regex. Order Roman numerals by length descending so that
# 'XXVIII' matches greedily before 'XX' or 'III'.
_ROMAN_ALT = '|'.join(sorted(ROMAN_TO_INT.keys(), key=len, reverse=True))
WCF_RE = re.compile(
    r'\bWCF\s+(' + _ROMAN_ALT + r')(\.[\d, \-–]*\d)?(?=\b|[^.\d])'
)

# Catechism Q. references. Tolerant of optional 'Q.', 'Q', and ranges.
LC_RE = re.compile(
    r'\b(?:Larger\s+Catechism|LC)\s+(?:Q\.?\s*)?(\d{1,3})(?:[\-–]\d{1,3})?\b'
)
SC_RE = re.compile(
    r'\b(?:Shorter\s+Catechism|SC)\s+(?:Q\.?\s*)?(\d{1,3})(?:[\-–]\d{1,3})?\b'
)


def find_citations(text):
    """Yield ``(start, end, kind, target, matched_text)`` for each citation.

    ``kind`` is one of ``'wcf'``, ``'wlc'``, ``'wsc'``.
    ``target`` is the chapter number (WCF) or question number (LC, SC).
    """
    if not text:
        return
    for m in WCF_RE.finditer(text):
        roman = m.group(1)
        n = ROMAN_TO_INT.get(roman)
        if n:
            yield (m.start(), m.end(), 'wcf', n, m.group(0))
    for m in LC_RE.finditer(text):
        n = int(m.group(1))
        if 1 <= n <= 196:
            yield (m.start(), m.end(), 'wlc', n, m.group(0))
    for m in SC_RE.finditer(text):
        n = int(m.group(1))
        if 1 <= n <= 107:
            yield (m.start(), m.end(), 'wsc', n, m.group(0))


def _url_for(kind, target):
    if kind == 'wcf':
        return reverse('westminster_standards:wcf_chapter',
                       kwargs={'number': target})
    if kind == 'wlc':
        return reverse('westminster_standards:catechism_question',
                       kwargs={'catechism_slug': 'wlc', 'number': target})
    if kind == 'wsc':
        return reverse('westminster_standards:catechism_question',
                       kwargs={'catechism_slug': 'wsc', 'number': target})
    return None


def linkify(text):
    """Return HTML with citations hyperlinked. Output is marked safe."""
    if not text:
        return mark_safe('')
    citations = sorted(find_citations(text), key=lambda c: c[0])
    if not citations:
        return mark_safe(escape(text))
    # Drop citations that overlap with an earlier one (defensive; in
    # practice the patterns don't overlap because each requires its own
    # prefix string).
    cleaned = []
    last_end = 0
    for c in citations:
        if c[0] >= last_end:
            cleaned.append(c)
            last_end = c[1]
    out = []
    cursor = 0
    for start, end, kind, target, matched in cleaned:
        out.append(escape(text[cursor:start]))
        url = _url_for(kind, target) or '#'
        out.append(f'<a class="ws-link" href="{url}">{escape(matched)}</a>')
        cursor = end
    out.append(escape(text[cursor:]))
    return mark_safe(''.join(out))


# ----------------------------------------------------------------------
# Reverse index — cached lazily.
# ----------------------------------------------------------------------

_INDEX = None


def _build_index():
    """Build ``{kind: {target: [crux_slug, ...]}}`` mapping by scanning
    each crux's ``language`` and ``references`` fields."""
    from .cruxes import CRUXES
    index = {'wcf': {}, 'wlc': {}, 'wsc': {}}
    for crux in CRUXES:
        seen = {'wcf': set(), 'wlc': set(), 'wsc': set()}
        sources = [crux.get('language', '') or '']
        sources.extend(crux.get('references', []) or [])
        for src in sources:
            for _, _, kind, target, _ in find_citations(src):
                if target in seen[kind]:
                    continue
                seen[kind].add(target)
                index[kind].setdefault(target, []).append(crux['slug'])
    return index


def get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    return _INDEX


def cruxes_for_wcf_chapter(number):
    """Return the list of cruxes (full dicts) that reference WCF chapter N."""
    from .cruxes import get_crux_by_slug
    slugs = get_index()['wcf'].get(number, [])
    return [get_crux_by_slug(s) for s in slugs if get_crux_by_slug(s)]


def cruxes_for_catechism_question(catechism_slug, number):
    from .cruxes import get_crux_by_slug
    slugs = get_index().get(catechism_slug, {}).get(number, [])
    return [get_crux_by_slug(s) for s in slugs if get_crux_by_slug(s)]


# ----------------------------------------------------------------------
# School mentions in crux legacy text — keyword-based matching.
# ----------------------------------------------------------------------

_SCHOOL_KEYWORDS = None


def _build_school_keywords():
    """Map keyword phrases to school slugs. Order by length descending
    so longer phrases match before shorter ones."""
    return sorted([
        ('Savoy Declaration', 'savoy-1658'),
        ('Savoy', 'savoy-1658'),
        ('1689 Particular Baptist', 'particular-baptists-1689'),
        ('Particular Baptist', 'particular-baptists-1689'),
        ('Second London Confession', 'particular-baptists-1689'),
        ('1788 American', 'american-1788-revision'),
        ('American revision', 'american-1788-revision'),
        ('American 1788', 'american-1788-revision'),
        ('American Presbyterian', 'american-1788-revision'),
        ('Free Church of Scotland', 'free-church-scotland-1843'),
        ('Free Church', 'free-church-scotland-1843'),
        ('Disruption', 'free-church-scotland-1843'),
        ('1843', 'free-church-scotland-1843'),
        ('Reformed Presbyterian', 'reformed-presbyterian-covenanters'),
        ('Covenanter', 'reformed-presbyterian-covenanters'),
        ('RPCNA', 'reformed-presbyterian-covenanters'),
        ('Marrow controversy', 'marrow-men'),
        ('Marrow men', 'marrow-men'),
        ('Marrow Men', 'marrow-men'),
        ('Boston', 'marrow-men'),
        ('Cumberland', 'cumberland-presbyterians'),
        ('OPC', 'opc-1936'),
        ('Orthodox Presbyterian', 'opc-1936'),
        ('PCA', 'pca-1973'),
        ('Presbyterian Church in America', 'pca-1973'),
        ('PCUSA', 'american-1788-revision'),
    ], key=lambda x: -len(x[0]))


def schools_mentioned_in_legacy(crux):
    """Return a deduplicated list of school slugs mentioned in a crux's
    legacy text, matched by keyword."""
    global _SCHOOL_KEYWORDS
    if _SCHOOL_KEYWORDS is None:
        _SCHOOL_KEYWORDS = _build_school_keywords()
    text = crux.get('legacy', '') or ''
    if not text:
        return []
    found = []
    seen = set()
    for keyword, slug in _SCHOOL_KEYWORDS:
        if keyword in text and slug not in seen:
            seen.add(slug)
            found.append(slug)
    return found
