"""Review scheduling for memorisation cards.

An SM-2 variant. The catechisms were written to be memorised — the Shorter
Catechism especially — so a review schedule is the natural companion to the
text: each answer comes back just before it would have been forgotten, and
the interval grows every time it is recalled.

The functions here are pure so the schedule can be tested without a database
or a clock.
"""

from datetime import timedelta

AGAIN = 'again'
HARD = 'hard'
GOOD = 'good'
EASY = 'easy'

GRADES = (AGAIN, HARD, GOOD, EASY)

GRADE_LABELS = {
    AGAIN: 'Forgot',
    HARD: 'Hard',
    GOOD: 'Knew it',
    EASY: 'Easy',
}

# SM-2 quality scores. Below 3 counts as a failure and restarts the interval.
_QUALITY = {AGAIN: 2, HARD: 3, GOOD: 4, EASY: 5}

MIN_EASE = 1.3
DEFAULT_EASE = 2.5
FIRST_INTERVAL_DAYS = 1
SECOND_INTERVAL_DAYS = 6
MAX_INTERVAL_DAYS = 365 * 2

# An answer recalled at three weeks or more is treated as known rather than
# still being learned; used for progress reporting, not for scheduling.
MATURE_INTERVAL_DAYS = 21


def next_ease(ease, grade):
    """The updated ease factor after a review, floored at ``MIN_EASE``."""
    quality = _QUALITY[grade]
    adjusted = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return round(max(MIN_EASE, adjusted), 4)


def next_interval(repetitions, interval_days, ease, grade):
    """Days until this card should come back."""
    if grade == AGAIN:
        return FIRST_INTERVAL_DAYS
    if repetitions == 0:
        return FIRST_INTERVAL_DAYS
    if repetitions == 1:
        return SECOND_INTERVAL_DAYS
    grown = interval_days * ease
    if grade == HARD:
        grown = interval_days * 1.2
    elif grade == EASY:
        grown = interval_days * ease * 1.3
    return min(MAX_INTERVAL_DAYS, max(FIRST_INTERVAL_DAYS, int(round(grown))))


def review(repetitions, interval_days, ease, grade, today):
    """Apply a review outcome.

    Returns ``(repetitions, interval_days, ease, due_on)``. A forgotten answer
    restarts the repetition count — it goes back to tomorrow — but keeps the
    (reduced) ease it has earned, so a card that has always been hard stays
    hard rather than starting from scratch.
    """
    if grade not in _QUALITY:
        raise ValueError(f'unknown grade {grade!r}')

    ease = next_ease(ease, grade)
    if grade == AGAIN:
        repetitions = 0
    interval = next_interval(repetitions, interval_days, ease, grade)
    if grade != AGAIN:
        repetitions += 1
    return repetitions, interval, ease, today + timedelta(days=interval)
