"""Stable references and citation export.

A reader citing the Confession writes "WCF 3.4", not "section 137" — but the
canonical URL is built from the sequential question number, so the human
reference was not addressable. These helpers resolve a reference to its
question and render the citation in the formats a reference manager reads.
"""

import re

CITATION_REFERENCE_RE = re.compile(r'^(?P<first>\d{1,3})(?:[.:](?P<second>\d{1,3}))?$')


def reference_for(question):
    """The human reference for a question: '3.4' for prose, '1' otherwise."""
    return question.display_number


def resolve_reference(catechism, reference):
    """Find the question a reference denotes, or None.

    Prose documents (confessions) take 'chapter.section'; catechisms take a
    bare question number.
    """
    match = CITATION_REFERENCE_RE.match((reference or '').strip())
    if not match:
        return None

    first = int(match.group('first'))
    second = match.group('second')

    if catechism.is_prose_document:
        if second is None:
            return None
        topic = catechism.topics.filter(order=first).first()
        if topic is None:
            return None
        number = topic.question_start + int(second) - 1
        if number > topic.question_end:
            return None
    else:
        if second is not None:
            return None
        number = first

    return catechism.questions.filter(number=number).first()


def citation_key(question):
    """A BibTeX-safe key, e.g. 'wcf-3-4'."""
    slug = question.catechism.slug
    return f"{slug}-{reference_for(question)}".replace('.', '-')


def citation_label(question):
    """How the reference reads in prose: 'WCF 3.4' or 'WSC 1'."""
    return f'{question.catechism.abbreviation} {reference_for(question)}'


def _part_title(question):
    if question.catechism.is_prose_document:
        chapter, _, section = reference_for(question).partition('.')
        return f'Chapter {chapter}, Section {section}'
    return f'Question {reference_for(question)}'


def citation_text(question, url=''):
    """A plain citation line for pasting into prose or a footnote."""
    catechism = question.catechism
    year = f' ({catechism.year})' if catechism.year else ''
    tail = f'. {url}' if url else ''
    return f'{catechism.name}{year}, {_part_title(question)}{tail}'


def bibtex(question, url='', accessed=None):
    """A BibTeX ``@incollection`` entry for this section or question."""
    catechism = question.catechism
    fields = [
        ('booktitle', f'{{{catechism.name}}}'),
        ('title', f'{{{_part_title(question)}}}'),
    ]
    if catechism.year:
        fields.append(('year', str(catechism.year)))
    if url:
        fields.append(('url', url))
    if accessed:
        fields.append(('urldate', f'{accessed:%Y-%m-%d}'))
    fields.append(('note', citation_label(question)))

    body = ',\n'.join(f'  {name:<10} = {{{value}}}' for name, value in fields)
    return f'@incollection{{{citation_key(question)},\n{body}\n}}\n'


def ris(question, url='', accessed=None):
    """An RIS record — the format Zotero, EndNote and Mendeley import."""
    catechism = question.catechism
    lines = [
        'TY  - CHAP',
        f'TI  - {_part_title(question)}',
        f'BT  - {catechism.name}',
    ]
    if catechism.year:
        lines.append(f'PY  - {catechism.year}')
    if url:
        lines.append(f'UR  - {url}')
    if accessed:
        lines.append(f'Y2  - {accessed:%Y/%m/%d}')
    lines += [f'N1  - {citation_label(question)}', 'ER  - ']
    return '\n'.join(lines) + '\n'
