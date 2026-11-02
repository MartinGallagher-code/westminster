"""Load the PCA Book of Church Order.

Sections are matched to the rows already in the database by their printed
reference ("21-4", "Preface II") and updated in place. The BCO is amended at
every General Assembly, so a reload routinely inserts sections (36-8 in 2026)
and shifts the sequential numbers that follow; deleting and recreating the
rows instead — as this command once did — cascaded through every reader's
notes, highlights, memorisation cards and reading positions on BCO sections,
and through the BCO cross-references, which ``load_bco_crossrefs`` then
skipped rebuilding because its own source file had not changed.
"""

import json
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils.text import slugify

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Question, Topic

SLUG = 'pca-bco'
VERSION_NAME = 'catechism-pca-bco'

# Before sections carried a ``reference``, the loader kept the section number
# in ``question_text`` ("21-4") and the preface sections' titles there.
LEGACY_PREFACE_TITLES = {
    'The King and Head of the Church': 'Preface I',
    'Preliminary Principles': 'Preface II',
    'The Constitution Defined': 'Preface III',
}
SECTION_NUMBER_RE = re.compile(r'^\d{1,2}-\d{1,2}$')
CHAPTER_NAME_RE = re.compile(r'^Chapter (\d+):')

# Moves every existing row clear of the numbers being assigned, so the
# ``(catechism, number)`` and ``(catechism, order)`` unique constraints never
# see two rows on the same value mid-reload.
RENUMBER_OFFSET = 100000


def data_paths():
    base = settings.BASE_DIR / 'data'
    return (base / 'pca_bco' / 'pca_bco.json', base / 'pca-bco_proof_texts.json')


def legacy_reference(question):
    """The printed reference of a row loaded before ``reference`` existed."""
    if question.reference:
        return question.reference
    text = (question.question_text or '').strip()
    if SECTION_NUMBER_RE.match(text):
        return text
    return LEGACY_PREFACE_TITLES.get(text, '')


def topic_slug(chapter, title):
    # Dashes and em dashes separate words in titles ("Officers—General").
    return slugify(f"ch-{chapter}-{re.sub(r'[-–—]', ' ', title)}")[:50].rstrip('-')


def build_plan(data, citations):
    """The topics and sections to load, in reading order."""
    topics = []

    def section(reference, heading, text):
        return {
            'reference': reference,
            'question_text': heading,
            'answer_text': text,
            'proof_texts': citations.get(reference, ''),
        }

    topics.append({
        'key': 'preface',
        'slug': 'preface',
        'name': 'Preface',
        'description': (
            'The King and Head of the Church, Preliminary Principles, '
            'and the Constitution Defined'
        ),
        'sections': [
            section(p['reference'], p['title'], p['text']) for p in data['preface']
        ],
    })

    for part in data['parts']:
        part_label = f"{part['part']} — {part['title']}"
        if part.get('introduction'):
            title = part.get('introduction_title', f"{part['title']}: Introduction")
            reference = 'Directory Preface' if part['part'] == 'Part III' else f"{part['part']} Preface"
            topics.append({
                'key': f"intro:{part['part']}",
                'slug': slugify(title)[:50].rstrip('-'),
                'name': title,
                'description': part_label,
                'sections': [section(reference, title, part['introduction'])],
            })
        for chapter in part['chapters']:
            if not chapter['sections']:
                continue  # Chapter 44 is vacated
            chapter_title = chapter['title']
            topics.append({
                'key': f"chapter:{chapter['chapter']}",
                'slug': topic_slug(chapter['chapter'], chapter_title),
                'name': f"Chapter {chapter['chapter']}: {chapter_title}",
                'description': part_label,
                'sections': [
                    section(
                        s['number'],
                        s.get('title') or s.get('division') or chapter_title,
                        s['text'],
                    )
                    for s in chapter['sections']
                ],
            })
    return topics


def _topic_key(topic):
    if topic.slug == 'preface':
        return 'preface'
    match = CHAPTER_NAME_RE.match(topic.name)
    if match:
        return f'chapter:{int(match.group(1))}'
    if topic.slug.startswith('preface-to-the-directory'):
        return 'intro:Part III'
    return f'slug:{topic.slug}'


class Command(BaseCommand):
    help = "Load PCA Book of Church Order chapters and sections into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Reload even if the source data has not changed',
        )

    def handle(self, *args, **options):
        paths = data_paths()
        data_path, citations_path = paths
        if not options['force'] and data_is_current(VERSION_NAME, *paths):
            self.stdout.write("PCA BCO data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)
        citations = {}
        if citations_path.exists():
            with open(citations_path) as f:
                citations = json.load(f)

        plan = build_plan(data, citations)
        total = sum(len(t['sections']) for t in plan)

        with transaction.atomic():
            summary = self._load(data, plan, total)

        mark_data_current(VERSION_NAME, *paths)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {total} PCA BCO sections ({data['edition']}): "
            f"{summary['updated']} updated in place, {summary['created']} added, "
            f"{summary['removed']} removed"
        ))
        if summary['removed_refs']:
            self.stdout.write(self.style.WARNING(
                "Removed sections no longer in the BCO: " + ", ".join(summary['removed_refs'])
            ))

    def _load(self, data, plan, total):
        description = (
            'The Book of Church Order of the Presbyterian Church in America, '
            'comprising the Form of Government, the Rules of Discipline, and '
            f"the Directory for the Worship of God. {data['edition']}. "
            f"{data.get('copyright', '')}"
        ).strip()
        catechism, _ = Catechism.objects.update_or_create(
            slug=SLUG,
            defaults={
                'name': 'Book of Church Order (PCA)',
                'abbreviation': 'BCO',
                'description': description,
                'year': data['year'],
                'total_questions': total,
                'document_type': Catechism.CONFESSION,
                'tradition': Catechism.WESTMINSTER,
                'uses_native_references': True,
            }
        )

        # Clear the way for renumbering (see RENUMBER_OFFSET).
        Question.objects.filter(catechism=catechism).update(number=F('number') + RENUMBER_OFFSET)
        Topic.objects.filter(catechism=catechism).update(
            order=F('order') + RENUMBER_OFFSET,
            question_start=F('question_start') + RENUMBER_OFFSET,
            question_end=F('question_end') + RENUMBER_OFFSET,
        )

        existing_topics = {}
        for topic in Topic.objects.filter(catechism=catechism):
            existing_topics.setdefault(_topic_key(topic), topic)

        # A row whose reference cannot be read, or repeats one already seen,
        # matches nothing and is removed below.
        existing_questions = {}
        for question in Question.objects.filter(catechism=catechism).order_by('number'):
            reference = legacy_reference(question)
            if reference and reference not in existing_questions:
                existing_questions[reference] = question

        seen_topics = set()
        seen_questions = set()
        updated = created = 0
        number = 0

        for order, entry in enumerate(plan, start=1):
            start = number + 1
            end = number + len(entry['sections'])
            topic = existing_topics.get(entry['key'])
            fields = {
                'name': entry['name'],
                'order': order,
                'question_start': start,
                'question_end': end,
                'description': entry['description'],
            }
            if topic is None:
                topic = Topic.objects.create(catechism=catechism, slug=entry['slug'], **fields)
            else:
                # Keep the existing slug: it is in readers' bookmarks and the
                # sitemap, and a retitled chapter is still the same chapter.
                for name, value in fields.items():
                    setattr(topic, name, value)
                topic.save()
            seen_topics.add(topic.pk)

            for section in entry['sections']:
                number += 1
                question = existing_questions.get(section['reference'])
                values = {
                    'number': number,
                    'topic': topic,
                    'reference': section['reference'],
                    'question_text': section['question_text'],
                    'answer_text': section['answer_text'],
                    'proof_texts': section['proof_texts'],
                }
                if question is None:
                    question = Question.objects.create(catechism=catechism, **values)
                    created += 1
                else:
                    for name, value in values.items():
                        setattr(question, name, value)
                    question.save()
                    updated += 1
                seen_questions.add(question.pk)

        stale_questions = Question.objects.filter(catechism=catechism).exclude(pk__in=seen_questions)
        removed_refs = [legacy_reference(q) or q.question_text[:20] for q in stale_questions]
        removed = stale_questions.count()
        stale_questions.delete()
        Topic.objects.filter(catechism=catechism).exclude(pk__in=seen_topics).delete()

        return {
            'updated': updated,
            'created': created,
            'removed': removed,
            'removed_refs': removed_refs,
        }
