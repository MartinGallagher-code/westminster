"""Compare the loaded Westminster text against an independent transcription.

Nobody should cite a transcription that has never been checked. The obvious
reference — a modern critical print edition — is not something this repository
can hold, so the check is against the *other* transcription the project
already carries: the Atlas app was ported with its own copy of the Confession
and both catechisms, sourced separately from the files under ``data/``.

Two independent transcriptions agreeing is real evidence. Where they disagree,
the divergence is either an error in one of them or a genuine edition
difference, and both want an editor's eye. This command finds and ranks them;
it does not adjudicate.

    python manage.py check_transcription
    python manage.py check_transcription --document wcf --threshold 0.98
"""

import difflib
import re

from django.core.management.base import BaseCommand, CommandError

from catechism.models import Question

DOCUMENTS = ('wcf', 'wlc', 'wsc')
DEFAULT_THRESHOLD = 0.995
DEFAULT_LIMIT = 20


def normalise(text):
    """Compare wording, not typesetting.

    Curly quotes, long dashes, hyphenation and whitespace differ between any
    two transcriptions of a seventeenth-century text and say nothing about
    whether the words match.
    """
    text = (text or '').lower()
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = re.sub(r'[‐-―]', '-', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def similarity(left, right):
    return difflib.SequenceMatcher(
        a=normalise(left).split(), b=normalise(right).split(), autojunk=False,
    ).ratio()


def word_pairs(left, right):
    """The (loaded, reference) word pairs that differ, for aggregation."""
    a, b = normalise(left).split(), normalise(right).split()
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    return [
        (' '.join(a[i1:i2]) or '—', ' '.join(b[j1:j2]) or '—')
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
        if tag != 'equal'
    ]


def word_differences(left, right, context=4):
    """The differing runs, with a little context, as readable strings."""
    a, b = normalise(left).split(), normalise(right).split()
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    notes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue
        before = ' '.join(a[max(0, i1 - context):i1])
        ours = ' '.join(a[i1:i2]) or '—'
        theirs = ' '.join(b[j1:j2]) or '—'
        notes.append(f'…{before} » loaded: “{ours}” / reference: “{theirs}”')
    return notes


class Command(BaseCommand):
    help = "Compare loaded Westminster text against the Atlas's transcription"

    def add_arguments(self, parser):
        parser.add_argument('--document', choices=DOCUMENTS, help='Check one document.')
        parser.add_argument(
            '--threshold', type=float, default=DEFAULT_THRESHOLD,
            help='Report sections below this similarity (default: %(default)s).',
        )
        parser.add_argument(
            '--limit', type=int, default=DEFAULT_LIMIT,
            help='Show at most this many divergences (default: %(default)s).',
        )
        parser.add_argument(
            '--summary', action='store_true',
            help='Group divergences by the differing words rather than listing '
                 'each section — turns dozens of findings into a few decisions.',
        )
        parser.add_argument(
            '--fail-on-divergence', action='store_true',
            help='Exit non-zero if anything falls below the threshold.',
        )

    def handle(self, *args, **options):
        documents = [options['document']] if options['document'] else list(DOCUMENTS)
        threshold = options['threshold']

        all_divergences = []
        for slug in documents:
            reference = self._reference_text(slug)
            if not reference:
                self.stderr.write(f'No reference transcription for {slug}; skipping.')
                continue

            divergences, compared, missing = self._compare(slug, reference, threshold)
            all_divergences.extend(divergences)

            self.stdout.write(
                f'{slug.upper()}: compared {compared} '
                f'item{"" if compared == 1 else "s"}, '
                f'{len(divergences)} below {threshold:.3f}'
                + (f', {missing} not found in the reference' if missing else '')
            )

        if all_divergences and options['summary']:
            self._write_summary(all_divergences)
        elif all_divergences:
            all_divergences.sort(key=lambda d: d['similarity'])
            self.stdout.write('')
            for divergence in all_divergences[:options['limit']]:
                self.stdout.write(self.style.WARNING(
                    f'{divergence["label"]} — {divergence["similarity"]:.3f}'
                ))
                for note in divergence['notes'][:4]:
                    self.stdout.write(f'    {note}')
            remaining = len(all_divergences) - options['limit']
            if remaining > 0:
                self.stdout.write(f'  … and {remaining} more.')

            if options['fail_on_divergence']:
                raise CommandError(
                    f'{len(all_divergences)} sections diverge from the reference'
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                'Both transcriptions agree everywhere checked.'
            ))

    def _write_summary(self, divergences):
        """One line per differing word pair, commonest first."""
        from collections import Counter

        counts = Counter(
            pair for divergence in divergences for pair in divergence['pairs']
        )
        self.stdout.write('')
        self.stdout.write(f'{len(counts)} distinct differences across '
                          f'{len(divergences)} sections:')
        for (ours, theirs), count in counts.most_common():
            self.stdout.write(
                f'  {count:>3} ×  loaded: “{ours}”  /  reference: “{theirs}”'
            )

    # ── comparison ────────────────────────────────────────────────────────

    def _reference_text(self, slug):
        """The Atlas's copy, keyed the same way the database is."""
        from westminster_standards.works import get_work_by_slug

        work = get_work_by_slug(slug)
        if not work:
            return {}

        if slug == 'wcf':
            return {
                (chapter['number'], section['number']): section['content']
                for chapter in work.get('chapters') or []
                for section in chapter.get('sections') or []
            }
        return {
            question['number']: f"{question['question']} {question['answer']}"
            for question in work.get('questions') or []
        }

    def _compare(self, slug, reference, threshold):
        divergences = []
        compared = 0
        missing = 0

        questions = Question.objects.filter(
            catechism__slug=slug,
        ).select_related('catechism', 'topic').order_by('number')

        for question in questions:
            if slug == 'wcf':
                if not question.topic:
                    continue
                key = (question.topic.order, question.number - question.topic.question_start + 1)
                ours = question.answer_text
            else:
                key = question.number
                ours = f'{question.question_text} {question.answer_text}'

            theirs = reference.get(key)
            if theirs is None:
                missing += 1
                continue

            compared += 1
            ratio = similarity(ours, theirs)
            if ratio < threshold:
                divergences.append({
                    'label': f'{slug.upper()} {question.display_number}',
                    'similarity': ratio,
                    'notes': word_differences(ours, theirs),
                    'pairs': word_pairs(ours, theirs),
                })
        return divergences, compared, missing
