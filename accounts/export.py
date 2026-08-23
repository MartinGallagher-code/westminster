"""Export a reader's own study material as Markdown.

Notes, annotations and highlights accumulate over years of study and are
worth more than the account that holds them. Markdown keeps them readable
anywhere and pastes cleanly into whatever the reader writes in.
"""

from collections import defaultdict

from .models import Highlight, InlineComment, UserNote


def _quote(text):
    """Render text as a Markdown blockquote."""
    lines = (text or '').strip().splitlines() or ['']
    return '\n'.join(f'> {line}'.rstrip() for line in lines)


def _question_heading(question):
    prefix = question.catechism.item_prefix
    return f'{prefix}{question.display_number}. {question.question_text}'.strip()


def notes_markdown(user, today, base_url=''):
    """The user's notes, annotations and highlights as a Markdown document.

    ``base_url`` is prepended to each question link so the export stands on
    its own outside the site; pass '' for site-relative links.
    """
    notes = list(
        UserNote.objects.filter(user=user)
        .select_related('question', 'question__catechism')
    )
    comments = list(
        InlineComment.objects.filter(user=user)
        .select_related('question', 'question__catechism', 'commentary__source')
    )
    highlights = list(
        Highlight.objects.filter(user=user)
        .select_related('commentary__source', 'commentary__question__catechism')
    )

    # Group everything by document, then by question.
    by_document = defaultdict(lambda: defaultdict(lambda: {
        'notes': [], 'comments': [], 'highlights': [],
    }))
    for note in notes:
        by_document[note.question.catechism][note.question]['notes'].append(note)
    for comment in comments:
        by_document[comment.question.catechism][comment.question]['comments'].append(comment)
    for highlight in highlights:
        question = highlight.commentary.question
        by_document[question.catechism][question]['highlights'].append(highlight)

    lines = [
        '# Study Reformed — my notes',
        '',
        f'Exported {today:%-d %B %Y} · {len(notes)} note{"" if len(notes) == 1 else "s"}, '
        f'{len(comments)} annotation{"" if len(comments) == 1 else "s"}, '
        f'{len(highlights)} highlight{"" if len(highlights) == 1 else "s"}.',
    ]
    if not (notes or comments or highlights):
        lines += ['', 'Nothing saved yet.']
        return '\n'.join(lines) + '\n'

    for catechism in sorted(by_document, key=lambda c: c.abbreviation):
        lines += ['', f'## {catechism.name}']
        questions = sorted(by_document[catechism], key=lambda q: q.number)
        for question in questions:
            entries = by_document[catechism][question]
            lines += [
                '',
                f'### {_question_heading(question)}',
                '',
                f'{base_url}{question.get_absolute_url()}',
            ]
            for note in entries['notes']:
                lines += [
                    '',
                    f'**Note** — updated {note.updated_at:%-d %B %Y}',
                    '',
                    _quote(note.text),
                ]
            for comment in entries['comments']:
                source = (
                    comment.commentary.source.name if comment.commentary
                    else comment.get_content_type_tag_display()
                )
                lines += [
                    '',
                    f'**Annotation** on “{comment.selected_text.strip()}” ({source})',
                    '',
                    _quote(comment.comment_text),
                ]
            for highlight in entries['highlights']:
                lines += [
                    '',
                    f'**Highlight** — {highlight.commentary.source.name}',
                    '',
                    _quote(highlight.selected_text),
                ]

    return '\n'.join(lines) + '\n'


def export_filename(today):
    return f'study-reformed-notes-{today:%Y-%m-%d}.md'
