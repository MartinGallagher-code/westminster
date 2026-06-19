"""Curation layer for the Westminster Standards teaching guide.

Each lesson is genuine teaching: written exposition that summarizes a doctrine
and sets it within the larger system of the Standards, with links out to the
specific questions and sections a reader can study for themselves. The prose
here is the teaching; the database supplies the texts it points to.

A ``text`` reference names a document by its catechism ``slug`` (e.g. ``wsc``)
and a list of question/section ``numbers``; the lesson view resolves these into
links. ``comparison_theme`` is the slug of an existing
:class:`~catechism.models.ComparisonTheme` for the "compare across the
standards" link.
"""

GUIDE_INTRO = {
    'title': 'A Teaching Guide to the Westminster Standards',
    'tagline': 'Read the doctrine in plain teaching, then study the texts for yourself.',
    'paragraphs': [
        (
            'The Westminster Standards — the Confession of Faith, the Larger Catechism, and '
            'the Shorter Catechism — set out one system of Reformed doctrine at three levels of '
            'depth. Read on their own, the questions and sections can feel like a list of answers '
            'to memorize without a thread running through them.'
        ),
        (
            'This guide supplies the thread. Each lesson is a short piece of teaching that explains '
            'a doctrine, shows where it sits in the wider corpus, and then points you to the exact '
            'questions and sections — with their Scripture proofs and historical commentary — so you '
            'can dig as deep as you like.'
        ),
    ],
}

# Lessons are grouped into units by the ``unit`` label; order within a unit
# follows the ``order`` field.
LESSONS = [
    {
        'slug': 'chief-end-of-man',
        'order': 1,
        'unit': 'Foundations',
        'title': 'The Chief End of Man',
        'aim': (
            'Understand why the Standards begin with the purpose of human life, and how that one '
            'answer frames everything they go on to teach.'
        ),
        'lead': (
            'Both Catechisms open with the same question — not about God, Scripture, or sin, but '
            'about us: what are human beings for? The answer they give is the hinge on which the '
            'rest of the system turns.'
        ),
        'sections': [
            {
                'heading': 'A question before all other questions',
                'body': [
                    (
                        'The Shorter and Larger Catechisms both begin by asking after the chief, or '
                        'highest, end of man — and answer that it is "to glorify God, and to enjoy him '
                        'forever." The placement is deliberate. Before the Standards say a word about '
                        'what we are to believe or how we are to live, they fix the goal toward which '
                        'all believing and living are aimed.'
                    ),
                    (
                        'This means the first answer is not really about us at all; it is about the God '
                        'for whom we exist. Everything that follows in the Catechisms — the knowledge of '
                        'God, his decrees, creation and providence, the work of Christ, salvation, the '
                        'law, the sacraments, and prayer — is an unfolding of how this single end is '
                        'first secured by God and then pursued by his people.'
                    ),
                ],
                'texts': [
                    {'catechism': 'wsc', 'numbers': [1]},
                    {'catechism': 'wlc', 'numbers': [1]},
                ],
            },
            {
                'heading': 'Glorifying and enjoying: one end, not two',
                'body': [
                    (
                        'The answer names two things — glorifying God and enjoying him — but the divines '
                        'intend one end, not two competing aims. To glorify God is to acknowledge and '
                        'display his worth; to enjoy him is to find one’s deepest satisfaction in him. '
                        'These are held together: the creature honours God precisely by delighting in him, '
                        'and finds its joy precisely in honouring him.'
                    ),
                    (
                        'The word "forever" carries weight too. The chief end is not only a present '
                        'vocation but an everlasting one, reaching its fullness in the life to come, when '
                        'the enjoyment of God is no longer mixed with sin or sorrow. The Catechism thus '
                        'opens with both a duty and a comfort in the same breath.'
                    ),
                ],
                'texts': [
                    {'catechism': 'wsc', 'numbers': [1]},
                ],
            },
            {
                'heading': 'Why it stands at the head of the system',
                'body': [
                    (
                        'Because the chief end is stated first, it governs how everything else is read. '
                        'The doctrine of God becomes the knowledge of the One we are made to glorify and '
                        'enjoy, not abstract speculation. The doctrine of sin becomes the account of how '
                        'that end was forfeited. Redemption in Christ is the recovery of the end, and the '
                        'means of grace — word, sacrament, and prayer — are the appointed ways the '
                        'redeemed pursue it.'
                    ),
                    (
                        'This is a characteristic Reformed instinct: that the chief end of man and the '
                        'chief end of God coincide. God acts for the sake of his own glory, and the '
                        'creature’s highest good is found in that same glory. Keeping the first '
                        'question in view stops the Standards from reading like a catalogue of doctrines '
                        'and holds them together as a single purpose.'
                    ),
                ],
                'texts': [
                    {'catechism': 'wlc', 'numbers': [1]},
                ],
            },
        ],
        'study_prompts': [
            'Read WSC Q1 and WLC Q1 together and ask what, if anything, the Larger Catechism adds.',
            'On the question pages, trace each Scripture proof and ask how it supports both glorifying '
            'and enjoying God.',
            'Read Watson on the Shorter Catechism’s first question and note how he treats enjoying '
            'God as the believer’s comfort, not only a duty.',
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
    """Return ``(previous, next)`` lesson dicts for navigation, or ``None`` at the ends."""
    for index, lesson in enumerate(LESSONS):
        if lesson['slug'] == slug:
            previous_lesson = LESSONS[index - 1] if index > 0 else None
            next_lesson = LESSONS[index + 1] if index < len(LESSONS) - 1 else None
            return previous_lesson, next_lesson
    return None, None
