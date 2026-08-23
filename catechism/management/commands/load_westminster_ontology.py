import json
from collections import defaultdict

from django.conf import settings
from django.core.management.base import BaseCommand

from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import (
    DoctrineHead, OntologyAttribute, OntologyLocus, Question,
    QuestionDoctrineHead, QuestionOntologyTag,
)


class Command(BaseCommand):
    help = "Load Westminster Standards Atlas ontology metadata"

    def handle(self, *args, **options):
        # The loci and attributes (and the hand-authored per-question attribute
        # tags) come from the JSON; the doctrine-head taxonomy is owned by the
        # Atlas app itself, so the module is part of this load's source data.
        from westminster_standards import heads_of_doctrine as atlas_heads

        data_path = settings.BASE_DIR / "data" / "westminster_ontology.json"
        heads_path = settings.BASE_DIR / "westminster_standards" / "heads_of_doctrine.py"
        version_key = "westminster-ontology"

        if data_is_current(version_key, data_path, heads_path):
            self.stdout.write("Westminster ontology unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        loci = {}
        attributes = {}
        for locus_data in data.get('loci', []):
            attrs = locus_data.get('attributes', [])
            locus, _ = OntologyLocus.objects.update_or_create(
                slug=locus_data['slug'],
                defaults={
                    'name': locus_data['name'],
                    'icon': locus_data.get('icon', ''),
                    'tagline': locus_data.get('tagline', ''),
                    'overview': locus_data.get('overview', ''),
                    'color': locus_data.get('color', ''),
                    'order': locus_data.get('order', 0),
                    'atlas_path': locus_data.get('atlas_path', ''),
                },
            )
            loci[locus.slug] = locus

            loaded_attr_slugs = set()
            for attr_data in attrs:
                attr, _ = OntologyAttribute.objects.update_or_create(
                    locus=locus,
                    slug=attr_data['slug'],
                    defaults={
                        'name': attr_data['name'],
                        'baseline_label': attr_data.get('baseline_label', ''),
                        'baseline_slug': attr_data.get('baseline_slug', ''),
                        'baseline_description': attr_data.get('baseline_description', ''),
                        'order': attr_data.get('order', 0),
                        'atlas_path': attr_data.get('atlas_path', ''),
                    },
                )
                loaded_attr_slugs.add(attr.slug)
                attributes[f'{locus.slug}:{attr.slug}'] = attr

            OntologyAttribute.objects.filter(locus=locus).exclude(
                slug__in=loaded_attr_slugs
            ).delete()

        heads = self._load_doctrine_heads(atlas_heads, loci)
        tag_count = self._load_attribute_tags(data, attributes)
        head_link_count = self._link_questions_to_heads(atlas_heads, heads)

        mark_data_current(version_key, data_path, heads_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(loci)} ontology loci, {len(attributes)} attributes, "
            f"{len(heads)} heads, {tag_count} question tags, and "
            f"{head_link_count} head links"
        ))

    def _load_doctrine_heads(self, atlas_heads, loci):
        """Mirror the Atlas's heads of doctrine into the database.

        The Atlas app (`westminster_standards.heads_of_doctrine`) is the single
        source of truth for the head taxonomy: its heads carry the ontology
        attributes they bear on, the text they cover, and a detail page at
        /atlas/heads/<slug>/. Mirroring them here — rather than maintaining a
        parallel list in the JSON — keeps the head chips on Study Reformed
        pages pointing at Atlas pages that actually exist.
        """
        heads = {}
        for head_data in atlas_heads.HEADS_OF_DOCTRINE:
            head, _ = DoctrineHead.objects.update_or_create(
                slug=head_data['slug'],
                defaults={
                    'name': head_data['name'],
                    'description': head_data.get('description', ''),
                    'locus': loci.get(head_data.get('locus_key')),
                    'order': head_data.get('number', 0),
                    'atlas_path': f"heads/{head_data['slug']}/",
                },
            )
            heads[head.slug] = head

        DoctrineHead.objects.exclude(slug__in=heads).delete()
        return heads

    def _load_attribute_tags(self, data, attributes):
        """Load the hand-authored per-question ontology attribute tags."""
        tag_count = 0
        for tag_data in data.get('question_tags', []):
            try:
                question = Question.objects.get(
                    catechism__slug=tag_data['catechism'],
                    number=tag_data['number'],
                )
            except Question.DoesNotExist:
                ref = f"{tag_data['catechism']} {tag_data['number']}"
                self.stderr.write(f"Question '{ref}' not found, skipping ontology links")
                continue

            attr_keys = set(tag_data.get('attributes', []))
            attr_ids = [
                attributes[key].id
                for key in attr_keys
                if key in attributes
            ]
            QuestionOntologyTag.objects.filter(question=question).exclude(
                attribute_id__in=attr_ids
            ).delete()
            for attr_key in attr_keys:
                attr = attributes.get(attr_key)
                if not attr:
                    self.stderr.write(f"Ontology attribute '{attr_key}' not found, skipping")
                    continue
                QuestionOntologyTag.objects.update_or_create(
                    question=question,
                    attribute=attr,
                    defaults={'is_representative': bool(tag_data.get('representative'))},
                )
                tag_count += 1
        return tag_count

    def _link_questions_to_heads(self, atlas_heads, heads):
        """Derive question -> doctrine-head links from the Atlas's coverage lists.

        Every Confession section and catechism question is covered by at least
        one head in the Atlas, so these links are complete for WCF/WLC/WSC
        without a separate hand-maintained mapping.
        """
        derived = defaultdict(set)

        catechism_questions = Question.objects.filter(
            catechism__slug__in=('wsc', 'wlc')
        ).select_related('catechism')
        for question in catechism_questions:
            for head in atlas_heads.heads_for_catechism_question(
                question.catechism.slug, question.number
            ):
                derived[question.id].add(head['slug'])

        confession_sections = Question.objects.filter(
            catechism__slug='wcf'
        ).select_related('topic')
        for question in confession_sections:
            if not question.topic:
                continue
            chapter = question.topic.order
            section = question.number - question.topic.question_start + 1
            for head in atlas_heads.heads_for_wcf_section(chapter, section):
                derived[question.id].add(head['slug'])

        head_link_count = 0
        for question_id, slugs in derived.items():
            head_ids = [heads[slug].id for slug in slugs if slug in heads]
            QuestionDoctrineHead.objects.filter(question_id=question_id).exclude(
                doctrine_head_id__in=head_ids
            ).delete()
            for head_id in head_ids:
                QuestionDoctrineHead.objects.update_or_create(
                    question_id=question_id,
                    doctrine_head_id=head_id,
                )
                head_link_count += 1
        return head_link_count
