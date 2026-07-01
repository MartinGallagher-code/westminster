"""Westminster questions — disputed questions debated at the Assembly.

Mirrors `puritans/questions.py` in shape. Candidate questions include:
the order of decrees, the extent of the atonement, the imputation of
active obedience, the polity question (Presbyterian/Independent/
Erastian), the regulative principle, the strict-Sabbath, the magistrate's
duty toward heresy, the identification of Antichrist, the bounds of
divorce, and the conscious intermediate state.

This file is intentionally stubbed at scaffold time.
"""


QUESTIONS = []
QUESTION_TAGS = {}
TAG_LABELS = {}


def get_question(slug):
    for q in QUESTIONS:
        if q.get('slug') == slug:
            return q
    return None


def assign_schools_to_stances(question, schools):
    """Placeholder matcher — full implementation will mirror
    puritans/questions.py's pattern-based assignment."""
    return []


def tags_for(slug):
    return QUESTION_TAGS.get(slug, [])


# Re-export ATTR_LABELS / ATTR_DIM so views can import them from here
# the same way puritans/views.py does.
from .data import ATTR_LABELS, ATTR_DIM  # noqa: F401,E402
