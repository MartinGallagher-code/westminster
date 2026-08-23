"""Snippet extraction and match highlighting for search results.

Results previously showed the opening words of a question and answer, which is
rarely where the match is: searching "assurance" against WLC 80 showed the
first dozen words of a long answer with the matched word nowhere in sight.
These helpers pick the window around the first match and mark the terms.
"""

import re

from django.utils.html import escape
from django.utils.safestring import mark_safe

SEARCH_STOP_WORDS = {
    'a', 'an', 'and', 'by', 'for', 'from', 'in', 'into', 'is', 'of', 'on',
    'or', 'the', 'to', 'with',
}

# Words either side of the match to keep in a snippet.
DEFAULT_RADIUS_WORDS = 14


def search_terms(query):
    """The meaningful words in a query, lowercased, stop words removed."""
    return [
        term for term in re.findall(r"[A-Za-z0-9']+", (query or '').lower())
        if len(term) > 2 and term not in SEARCH_STOP_WORDS
    ]


def _term_pattern(query):
    """A regex matching any query term at a word start, longest term first.

    Matching at a word *start* rather than anywhere means "faith" highlights
    "faithful" (the search engine stems, so it matched that row) without
    "sin" lighting up every "since" and "business".
    """
    terms = search_terms(query)
    phrase = (query or '').strip()
    candidates = sorted({phrase.lower(), *terms} - {''}, key=len, reverse=True)
    if not candidates:
        return None
    return re.compile(
        r'\b(' + '|'.join(re.escape(term) for term in candidates) + r')',
        re.IGNORECASE,
    )


def snippet(text, query, radius_words=DEFAULT_RADIUS_WORDS):
    """Plain-text window of ``text`` centred on the first match of ``query``.

    Works on whole words so a prefix match never splits the word it matched
    ("faith" inside "faithful" keeps the word intact). Falls back to the
    opening words when nothing matches, so a result always shows something.
    """
    words = (text or '').split()
    if not words:
        return ''

    pattern = _term_pattern(query)
    index = None
    if pattern is not None:
        index = next(
            (i for i, word in enumerate(words) if pattern.search(word)), None,
        )

    if index is None:
        head = words[:radius_words * 2]
        return ' '.join(head) + (' …' if len(words) > len(head) else '')

    start = max(0, index - radius_words)
    stop = min(len(words), index + radius_words + 1)
    return (
        ('… ' if start > 0 else '')
        + ' '.join(words[start:stop])
        + (' …' if stop < len(words) else '')
    )


def highlight(text, query):
    """HTML-escape ``text`` and mark each query term.

    Uses its own class so search hits are visually distinct from a reader's
    saved highlights, which also render as ``<mark>``.
    """
    escaped = escape(text or '')
    pattern = _term_pattern(query)
    if pattern is None:
        return mark_safe(escaped)
    # Escaping happens first, so the pattern runs over entity-safe text; the
    # terms themselves cannot introduce markup because they are escaped too.
    return mark_safe(pattern.sub(r'<mark class="search-hit">\1</mark>', escaped))


def highlighted_snippet(text, query, radius_words=DEFAULT_RADIUS_WORDS):
    """A snippet around the first match, escaped, with the terms marked."""
    return highlight(snippet(text, query, radius_words), query)
