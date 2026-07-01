"""Format scripture-proof references for display.

The two catechisms arrived in different citation styles:

  * Larger Catechism — OSIS-style codes: ``Rom.11.36``, ``Ps.73.24-Ps.73.28``,
    ``Luke.16.29,Luke.16.31``, ``Heb.8-Heb.10``.
  * Shorter Catechism — already human-readable: ``Rom. 11:36``,
    ``I Cor. 6:20; 10:31``, ``II Pet.1:20-21; 3:2, 15-16``.

``pretty_ref`` converts the OSIS style into the same readable style the
Shorter Catechism uses (and lightly normalises the Shorter Catechism's
Roman book-numerals to Arabic), so the proof apparatus reads consistently
across both. It is conservative: any reference it cannot fully parse is
returned unchanged, so an unexpected pattern degrades to the source text
rather than being mangled.
"""

import re

# OSIS book code -> display abbreviation.
OSIS_BOOKS = {
    'Gen': 'Gen.', 'Exod': 'Exod.', 'Lev': 'Lev.', 'Num': 'Num.',
    'Deut': 'Deut.', 'Josh': 'Josh.', 'Judg': 'Judg.', 'Ruth': 'Ruth',
    '1Sam': '1 Sam.', '2Sam': '2 Sam.', '1Kgs': '1 Kings', '2Kgs': '2 Kings',
    '1Chr': '1 Chron.', '2Chr': '2 Chron.', 'Ezra': 'Ezra', 'Neh': 'Neh.',
    'Esth': 'Esth.', 'Job': 'Job', 'Ps': 'Ps.', 'Prov': 'Prov.',
    'Eccl': 'Eccl.', 'Song': 'Song', 'Isa': 'Isa.', 'Jer': 'Jer.',
    'Lam': 'Lam.', 'Ezek': 'Ezek.', 'Dan': 'Dan.', 'Hos': 'Hos.',
    'Joel': 'Joel', 'Amos': 'Amos', 'Obad': 'Obad.', 'Jonah': 'Jonah',
    'Mic': 'Mic.', 'Nah': 'Nah.', 'Hab': 'Hab.', 'Zeph': 'Zeph.',
    'Hag': 'Hag.', 'Zech': 'Zech.', 'Mal': 'Mal.', 'Matt': 'Matt.',
    'Mark': 'Mark', 'Luke': 'Luke', 'John': 'John', 'Acts': 'Acts',
    'Rom': 'Rom.', '1Cor': '1 Cor.', '2Cor': '2 Cor.', 'Gal': 'Gal.',
    'Eph': 'Eph.', 'Phil': 'Phil.', 'Col': 'Col.', '1Thess': '1 Thess.',
    '2Thess': '2 Thess.', '1Tim': '1 Tim.', '2Tim': '2 Tim.',
    'Titus': 'Titus', 'Phlm': 'Philem.', 'Heb': 'Heb.', 'Jas': 'James',
    '1Pet': '1 Pet.', '2Pet': '2 Pet.', '1John': '1 John', '2John': '2 John',
    '3John': '3 John', 'Jude': 'Jude', 'Rev': 'Rev.',
}

_NDASH = '–'

_OSIS_TOKEN = re.compile(r'^([1-3]?[A-Za-z]+)\.(\d+)(?:\.(\d+))?$')
_LOOKS_OSIS = re.compile(r'^[1-3]?[A-Za-z]+\.\d')
_LEADING_ROMAN = re.compile(r'^(III|II|I)\s+(?=[A-Z])')
_ROMAN_TO_ARABIC = {'I': '1', 'II': '2', 'III': '3'}


def _parse_token(tok):
    """Parse an OSIS token into ``(book, chapter, verse_or_None)`` or None."""
    m = _OSIS_TOKEN.match(tok.strip())
    if not m:
        return None
    book, chap, verse = m.group(1), int(m.group(2)), m.group(3)
    if book not in OSIS_BOOKS:
        return None
    return (book, chap, int(verse) if verse is not None else None)


def _fmt(book, chap, verse):
    b = OSIS_BOOKS[book]
    return f"{b} {chap}" if verse is None else f"{b} {chap}:{verse}"


def _segment(seg):
    """Parse one comma-free OSIS segment into a dict with the full rendered
    form and, when it is a plain verse reference, a bare ``verse`` string that
    may be used when the book and chapter repeat the previous segment.
    Returns None if the segment cannot be parsed."""
    if '-' in seg:
        a, _, b = seg.partition('-')
        pa, pb = _parse_token(a), _parse_token(b)
        if not pa or not pb:
            return None
        (ba, ca, va), (bb, cb, vb) = pa, pb
        if ba != bb:                                   # cross-book range
            return {'book': ba, 'chap': ca,
                    'full': f"{_fmt(*pa)}{_NDASH}{_fmt(*pb)}", 'verse': None}
        if va is None and vb is None:                  # chapter range
            return {'book': ba, 'chap': None,
                    'full': f"{OSIS_BOOKS[ba]} {ca}{_NDASH}{cb}", 'verse': None}
        if ca == cb:                                   # verse range in a chapter
            return {'book': ba, 'chap': ca,
                    'full': f"{_fmt(ba, ca, va)}{_NDASH}{vb}",
                    'verse': f"{va}{_NDASH}{vb}"}
        return {'book': ba, 'chap': ca,                # cross-chapter range
                'full': f"{_fmt(ba, ca, va)}{_NDASH}{cb}:{vb}", 'verse': None}
    p = _parse_token(seg)
    if not p:
        return None
    book, chap, verse = p
    if verse is None:
        return {'book': book, 'chap': chap, 'full': _fmt(book, chap, None),
                'verse': None}
    return {'book': book, 'chap': chap, 'full': _fmt(book, chap, verse),
            'verse': str(verse)}


def pretty_ref(raw):
    """Return a readable form of a single proof reference string."""
    if not raw:
        return raw
    raw = raw.strip()
    if not _LOOKS_OSIS.match(raw):
        # Shorter-Catechism style: already readable; just convert a leading
        # Roman book-numeral (I/II/III) to Arabic to match the OSIS output.
        return _LEADING_ROMAN.sub(
            lambda m: _ROMAN_TO_ARABIC[m.group(1)] + ' ', raw)
    parts = []
    prev_book = prev_chap = None
    for seg in raw.split(','):
        d = _segment(seg.strip())
        if d is None:
            return raw            # conservative fallback — leave untouched
        if d['verse'] is not None and d['book'] == prev_book and d['chap'] == prev_chap:
            parts.append(d['verse'])          # same book+chapter — bare verse
        else:
            parts.append(d['full'])
        prev_book, prev_chap = d['book'], d['chap']
    return ', '.join(parts)
