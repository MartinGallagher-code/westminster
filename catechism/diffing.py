"""Word-level diff between parallel sections of related confessions.

The Savoy Declaration (1658) and the Second London Baptist Confession (1689)
are revisions of the Westminster Confession (1646), and the interesting parts
are the edits: a clause dropped from the chapter on the civil magistrate, a
sentence added on the church. Set side by side the texts look identical and
the changes are easy to miss. Diffed, the revision *is* the reading.
"""

import difflib
import re

EQUAL = 'equal'
INSERTED = 'inserted'
DELETED = 'deleted'

# Split into words while keeping the whitespace and punctuation that follow
# them, so a rebuilt diff reads as prose rather than as a token list.
_TOKEN_RE = re.compile(r'\S+\s*')


def _tokenise(text):
    return _TOKEN_RE.findall(text or '')


def _normalise(token):
    """Compare on words alone: punctuation and case were modernised freely."""
    return re.sub(r'[^\w]', '', token).lower()


def diff_words(before, after):
    """Segments of ``(op, text)`` turning ``before`` into ``after``."""
    left, right = _tokenise(before), _tokenise(after)
    matcher = difflib.SequenceMatcher(
        a=[_normalise(t) for t in left],
        b=[_normalise(t) for t in right],
        autojunk=False,
    )

    segments = []

    def append(op, text):
        if not text:
            return
        if segments and segments[-1][0] == op:
            segments[-1] = (op, segments[-1][1] + text)
        else:
            segments.append((op, text))

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            append(EQUAL, ''.join(right[j1:j2]))
        elif tag == 'delete':
            append(DELETED, ''.join(left[i1:i2]))
        elif tag == 'insert':
            append(INSERTED, ''.join(right[j1:j2]))
        else:                                    # replace
            append(DELETED, ''.join(left[i1:i2]))
            append(INSERTED, ''.join(right[j1:j2]))
    return segments


def change_ratio(segments):
    """Share of the text that changed, 0.0–1.0 — for a per-section summary."""
    total = sum(len(text) for _op, text in segments)
    if not total:
        return 0.0
    changed = sum(len(text) for op, text in segments if op != EQUAL)
    return round(changed / total, 3)


def align_sections(left_questions, right_questions):
    """Pair parallel sections positionally, padding the shorter side.

    These confessions are structurally parallel — chapter for chapter, section
    for section — so position is the alignment. Where one has a section the
    other lacks, it shows as a whole-section addition or removal, which is
    itself the substantive difference.
    """
    pairs = []
    for index in range(max(len(left_questions), len(right_questions))):
        left = left_questions[index] if index < len(left_questions) else None
        right = right_questions[index] if index < len(right_questions) else None
        pairs.append((left, right))
    return pairs


def section_text(question):
    """The text of a section for diffing: the answer, or the Q and A together."""
    if question is None:
        return ''
    if question.catechism.is_prose_document:
        return question.answer_text or question.question_text or ''
    return f'{question.question_text} {question.answer_text}'.strip()


def build_diff(left_questions, right_questions):
    """A diff row per aligned section pair."""
    rows = []
    for left, right in align_sections(list(left_questions), list(right_questions)):
        segments = diff_words(section_text(left), section_text(right))
        rows.append({
            'left': left,
            'right': right,
            'segments': segments,
            'change_ratio': change_ratio(segments),
            'unchanged': all(op == EQUAL for op, _text in segments) and bool(segments),
        })
    return rows
