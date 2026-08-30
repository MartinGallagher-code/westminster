"""Recognise Scripture references typed into the search box.

Searching "Rom 8:30" used to run a substring match over question and answer
text, which is almost never what the reader wants — the reference itself
lives in the proof-text apparatus, and the Scripture index already answers
"what cites this passage?". These helpers spot a reference so the search view
can route there instead.

A reference is only recognised when a chapter number is present. Several book
names are ordinary English words — Job, Acts, Judges, Kings, Numbers — and a
bare "acts" is far more likely to be a word search than a request for the book.
"""

import re
from urllib.parse import urlencode

# "1 Cor 13:4-7", "1Cor 13", "I Corinthians 13:4", "Rom 8"
_REFERENCE_RE = re.compile(
    r"""^
    (?P<book>(?:[123]\s*)?[A-Za-z]+(?:\s+[A-Za-z]+)*?)
    \s*
    (?P<chapter>\d{1,3})
    (?:\s*[:.]\s*(?P<verse>\d{1,3}(?:\s*[-–]\s*\d{1,3})?))?
    $""",
    re.VERBOSE,
)

_LEADING_ORDINAL = {
    'i': '1', 'ii': '2', 'iii': '3',
    'first': '1', 'second': '2', 'third': '3',
}

MIN_PREFIX_LENGTH = 3


def _normalise(text):
    """Lowercase, drop full stops, collapse whitespace, digitise ordinals."""
    cleaned = re.sub(r'\.', ' ', (text or '').strip().lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    parts = cleaned.split(' ')
    if parts and parts[0] in _LEADING_ORDINAL:
        parts[0] = _LEADING_ORDINAL[parts[0]]
    cleaned = ' '.join(parts)
    # "1cor" -> "1 cor"
    return re.sub(r'^([123])\s*([a-z])', r'\1 \2', cleaned)


def _book_key(value):
    return _normalise(value).replace(' ', '')


def _resolve_book(name, books):
    """Find the one book ``name`` denotes, or None if absent or ambiguous."""
    key = _book_key(name)
    if not key:
        return None

    for book in books:
        if key in {_book_key(book.name), _book_key(book.abbreviation), _book_key(book.slug)}:
            return book

    if len(key) < MIN_PREFIX_LENGTH:
        return None
    matches = [book for book in books if _book_key(book.name).startswith(key)]
    # "Phil" is a prefix of both Philippians and Philemon: ambiguous, so leave
    # it to the text search rather than guessing.
    return matches[0] if len(matches) == 1 else None


def parse_scripture_reference(query, books=None):
    """Resolve ``query`` to a Scripture reference, or None.

    Returns ``{'book', 'chapter', 'verse', 'label', 'ref'}`` where ``ref`` is
    the canonical "8:30" / "8" fragment used to filter the book page.
    """
    text = _normalise(query)
    if not text:
        return None
    match = _REFERENCE_RE.match(text)
    if not match:
        return None

    if books is None:
        from .models import BibleBook
        books = list(BibleBook.objects.all())

    book = _resolve_book(match.group('book'), books)
    if book is None:
        return None

    chapter = int(match.group('chapter'))
    verse = match.group('verse')
    verse = re.sub(r'\s*[-–]\s*', '-', verse) if verse else None
    ref = f'{chapter}:{verse}' if verse else str(chapter)
    label = f'{book.name} {ref}'
    return {'book': book, 'chapter': chapter, 'verse': verse, 'label': label, 'ref': ref}


def chapter_from_ref(ref):
    """The chapter number in a '8' or '8:30' fragment, or None."""
    match = re.match(r'^(\d{1,3})', (ref or '').strip())
    return int(match.group(1)) if match else None


def reference_matches_chapter(reference, chapter):
    """Whether an index entry's reference string cites ``chapter``.

    Entries look like "Rom 8:29-30", "Romans 8", or "8:30"; match the chapter
    number where a chapter can appear rather than anywhere in the string, so
    chapter 8 does not match "Rom 1:8".
    """
    if chapter is None:
        return True
    return re.search(rf'(?<!\d)(?<![:.]){chapter}(?![\d])(?=\s*[:.]|\s*$|\s*[,;])',
                     reference or '') is not None


# A proof text often cites several verses at once — "1 Cor. 10:16, 17, 21",
# "1 Cor. 11:23 to 29", "1 Cor. 11:27 to the end, with Jude 23". The book page
# filters by chapter, so the leading citation is enough to land the reader in
# the right place; everything from the first continuation marker on is dropped.
_CONTINUATION_RE = re.compile(r'\s*(?:[,;&]|\bto\b|\bwith\b|\band\b|\bcf\b|\bff?\b)')


def _leading_citation(reference):
    """The first citation in a multi-verse proof text, or None if it is alone."""
    head = _CONTINUATION_RE.split(reference, maxsplit=1)[0].strip()
    return head if head and head != reference.strip() else None


def scripture_urls(references, books=None):
    """Map each reference to the Scripture-index page that lists its citations.

    Proof texts are stored as display strings ("1 Cor. 10:31", "Ps. 73:25-28").
    Rendering them as inert text strands the reader: the site already knows
    which questions cite a passage, and the book page answers that. Resolve the
    references in bulk — one ``BibleBook`` fetch for the whole page rather than
    one per proof — and skip anything the parser cannot place, so a reference
    is either a working link or plain text, never a dead affordance.

    The link always carries the reference as written in ``?from=``, so the book
    page can offer it back even where only its leading citation resolved.
    """
    references = [ref for ref in (references or []) if ref]
    if not references:
        return {}

    if books is None:
        from .models import BibleBook
        books = list(BibleBook.objects.all())

    urls = {}
    for ref in references:
        if ref in urls:
            continue
        parsed = parse_scripture_reference(ref, books=books)
        if parsed is None:
            head = _leading_citation(ref)
            parsed = parse_scripture_reference(head, books=books) if head else None
        if parsed is None:
            continue
        query = urlencode({'ref': parsed['ref'], 'from': ref})
        urls[ref] = f"{parsed['book'].get_absolute_url()}?{query}"
    return urls
