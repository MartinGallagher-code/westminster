"""Curation layer for the Westminster Standards teaching guide.

This is a thin, version-controlled curation file that sequences content the
site already holds — questions, Scripture proofs, historical commentaries,
cross-references, and comparison themes — into ordered lessons. It introduces
no new source material and no database models: the lesson view resolves the
references below against the data already loaded in the database.

A reading references a document by its catechism ``slug`` (e.g. ``wsc``) and a
list of question/section ``numbers``. ``comparison_theme`` is the slug of an
existing :class:`~catechism.models.ComparisonTheme` for the "compare across the
standards" link. Everything else is plain prose curated here.
"""

GUIDE_INTRO = {
    'title': 'A Teaching Guide to the Westminster Standards',
    'tagline': 'A guided path through the Confession and Catechisms, lesson by lesson.',
    'paragraphs': [
        (
            'The Westminster Standards — the Confession of Faith, the Larger Catechism, and '
            'the Shorter Catechism — set out one system of Reformed doctrine at three levels of '
            'depth. The Shorter Catechism gives the memorable core, the Larger Catechism expands '
            'it for fuller instruction, and the Confession states it systematically for the church.'
        ),
        (
            'This guide walks through that teaching one lesson at a time. Each lesson gathers the '
            'relevant questions and sections side by side, shows the Scripture proofs the divines '
            'cited, opens the historical commentaries, and links out to compare the same doctrine '
            'across the wider Reformed confessions.'
        ),
    ],
}

# Lessons are grouped into units purely by the ``unit`` label; order within a
# unit follows the ``order`` field. Add lessons here as the guide grows.
LESSONS = [
    {
        'slug': 'chief-end-of-man',
        'order': 1,
        'unit': 'Foundations',
        'title': 'The Chief End of Man',
        'aim': (
            'Begin where the Standards begin: with the purpose for which God made us, and why '
            'that purpose frames everything the Catechisms go on to teach.'
        ),
        'overview': (
            'The very first question of both Catechisms asks what human beings are for. The answer '
            '— to glorify God and to enjoy him forever — is not merely an opening formality but the '
            'lens through which the whole system of doctrine is read. Glory and enjoyment are held '
            'together: God is to be honoured, and in honouring him we find our highest good.'
        ),
        'readings': [
            {'catechism': 'wsc', 'numbers': [1]},
            {'catechism': 'wlc', 'numbers': [1]},
        ],
        'study_prompts': [
            'Notice that the Shorter and Larger Catechisms open with almost the same words — read '
            'them together and ask what the Larger Catechism adds.',
            'Trace each Scripture proof and ask how it supports both halves of the answer: glorifying '
            'God and enjoying him.',
            'Read Watson on this question and note how he treats "enjoying God forever" as the '
            'believer’s comfort, not only a duty.',
        ],
        'comparison_theme': 'mans-chief-end-and-holy-scripture',
    },
]


def get_guide_intro():
    return GUIDE_INTRO


def get_lessons():
    return LESSONS


def get_lesson(slug):
    for lesson in LESSONS:
        if lesson['slug'] == slug:
            return lesson
    return None


def get_adjacent_lessons(slug):
    """Return ``(previous, next)`` lesson dicts for navigation, or ``None`` ends."""
    for index, lesson in enumerate(LESSONS):
        if lesson['slug'] == slug:
            previous_lesson = LESSONS[index - 1] if index > 0 else None
            next_lesson = LESSONS[index + 1] if index < len(LESSONS) - 1 else None
            return previous_lesson, next_lesson
    return None, None
