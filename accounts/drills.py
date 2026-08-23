"""Ways of drilling an answer you are trying to learn by heart.

Reading an answer and deciding you knew it is the weakest form of practice —
recognition feels like recall. These give the reader progressively less to lean
on: the shape of the words, then most of them, then nothing at all.

Pure functions, so the drills can be tested without a database, a browser, or a
clock. Rendering belongs to the templates.
"""

import random
import re
from difflib import SequenceMatcher

from catechism.diffing import normalise_word

RECALL = 'recall'
INITIALS = 'initials'
CLOZE = 'cloze'
TYPE = 'type'

MODES = (
    (RECALL, 'Read and recall', 'Reveal the answer and say how it went.'),
    (INITIALS, 'First letters', 'Only the first letter of each word is shown.'),
    (CLOZE, 'Fill the gaps', 'Some words are removed; supply them from memory.'),
    (TYPE, 'Type it out', 'Write the answer and have it checked word by word.'),
)
MODE_KEYS = tuple(mode for mode, _label, _help in MODES)

DEFAULT_CLOZE_RATIO = 0.35
MIN_CLOZE_WORD_LENGTH = 4


def first_letters(text):
    """The answer reduced to its shape: first letter of each word kept.

    "Man's chief end" becomes "M__'_ c____ e__" — enough to carry the rhythm
    of the sentence without giving the words away.
    """
    def reduce(token):
        return token[:1] + ''.join(
            '_' if character.isalnum() else character for character in token[1:]
        )

    return ' '.join(reduce(token) for token in (text or '').split())


def cloze(text, seed, ratio=DEFAULT_CLOZE_RATIO):
    """Blank a deterministic share of the words.

    Deterministic so the same card shows the same gaps if the page is
    reloaded — a drill that reshuffles under you is a different drill. Short
    words are left in place: blanking "of" teaches nothing.
    """
    tokens = (text or '').split()
    candidates = [
        index for index, token in enumerate(tokens)
        if len(normalise_word(token)) >= MIN_CLOZE_WORD_LENGTH
    ]
    if not candidates:
        return [{'text': token, 'blank': False} for token in tokens]

    count = max(1, round(len(candidates) * ratio))
    chosen = set(random.Random(seed).sample(candidates, min(count, len(candidates))))
    return [
        {'text': token, 'blank': index in chosen}
        for index, token in enumerate(tokens)
    ]


def _words(text):
    return [token for token in re.split(r'\s+', (text or '').strip()) if token]


def score_typed(expected, typed):
    """Compare what was typed against the answer, word by word.

    Returns the accuracy, a marked-up rendering of the expected answer, and
    any words typed that do not belong. Comparison ignores case and
    punctuation: a reader who types "mans" for "Man's" has remembered it.
    """
    expected_words = _words(expected)
    typed_words = _words(typed)

    matcher = SequenceMatcher(
        a=[normalise_word(word) for word in expected_words],
        b=[normalise_word(word) for word in typed_words],
        autojunk=False,
    )

    marked = []
    extras = []
    correct = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            correct += i2 - i1
            marked.extend(
                {'text': word, 'status': 'correct'} for word in expected_words[i1:i2]
            )
        elif tag == 'delete':
            marked.extend(
                {'text': word, 'status': 'missing'} for word in expected_words[i1:i2]
            )
        elif tag == 'insert':
            extras.extend(typed_words[j1:j2])
        else:
            marked.extend(
                {'text': word, 'status': 'wrong'} for word in expected_words[i1:i2]
            )
            extras.extend(typed_words[j1:j2])

    denominator = max(len(expected_words), len(typed_words)) or 1
    accuracy = round(correct / denominator, 4)
    return {
        'accuracy': accuracy,
        'percentage': int(round(accuracy * 100)),
        'marked': marked,
        'extras': extras,
        'expected_words': len(expected_words),
        'correct_words': correct,
        'is_perfect': accuracy == 1.0 and bool(expected_words),
    }


def suggested_grade(accuracy):
    """Which button to recommend after a typed attempt.

    A recommendation only — the reader knows whether it came back easily or
    was dragged up word by word, and that is what the schedule needs.
    """
    from .scheduling import AGAIN, EASY, GOOD, HARD

    if accuracy >= 0.99:
        return EASY
    if accuracy >= 0.9:
        return GOOD
    if accuracy >= 0.7:
        return HARD
    return AGAIN
