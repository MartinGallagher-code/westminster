"""Curation layer for the Westminster Standards teaching guide.

Each lesson is genuine teaching: written exposition that summarizes a doctrine
and sets it within the larger system of the Standards, with links out to the
specific questions and sections a reader can study for themselves. The prose
lives in ``data/teaching_guide.json`` (alongside the project's other source
data); this module loads it and resolves lessons by slug.

A ``text`` reference names a document by its catechism ``slug`` (e.g. ``wsc``)
and a list of question/section ``numbers``; the lesson view resolves these into
links. ``comparison_theme`` is the slug of an existing
:class:`~catechism.models.ComparisonTheme` for the "compare across the
standards" link.
"""

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings

_DATA_PATH = Path(settings.BASE_DIR) / 'data' / 'teaching_guide.json'


@lru_cache(maxsize=1)
def _load():
    with open(_DATA_PATH, encoding='utf-8') as handle:
        data = json.load(handle)
    intro = data.get('intro', {})
    lessons = sorted(data.get('lessons', []), key=lambda lesson: lesson.get('order', 0))
    return intro, lessons


def get_guide_intro():
    return _load()[0]


def get_lessons():
    return _load()[1]


def get_lesson(slug):
    for lesson in get_lessons():
        if lesson['slug'] == slug:
            return lesson
    return None


def get_adjacent_lessons(slug):
    """Return ``(previous, next)`` lesson dicts for navigation, or ``None`` at the ends."""
    lessons = get_lessons()
    for index, lesson in enumerate(lessons):
        if lesson['slug'] == slug:
            previous_lesson = lessons[index - 1] if index > 0 else None
            next_lesson = lessons[index + 1] if index < len(lessons) - 1 else None
            return previous_lesson, next_lesson
    return None, None
