import json

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
        data_path = settings.BASE_DIR / "data" / "westminster_ontology.json"
        version_key = "westminster-ontology"

        if data_is_current(version_key, data_path):
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

        heads = {}
        loaded_head_slugs = set()
        for head_data in data.get('doctrine_heads', []):
            head, _ = DoctrineHead.objects.update_or_create(
                slug=head_data['slug'],
                defaults={
                    'name': head_data['name'],
                    'description': head_data.get('description', ''),
                    'locus': loci.get(head_data.get('locus')),
                    'order': head_data.get('order', 0),
                    'atlas_path': head_data.get('atlas_path', ''),
                },
            )
            heads[head.slug] = head
            loaded_head_slugs.add(head.slug)

        DoctrineHead.objects.exclude(slug__in=loaded_head_slugs).delete()

        tag_count = 0
        head_link_count = 0
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

            head_slugs = set(tag_data.get('heads', []))
            head_ids = [
                heads[head_slug].id
                for head_slug in head_slugs
                if head_slug in heads
            ]
            QuestionDoctrineHead.objects.filter(question=question).exclude(
                doctrine_head_id__in=head_ids
            ).delete()
            for head_slug in head_slugs:
                head = heads.get(head_slug)
                if not head:
                    self.stderr.write(f"Doctrine head '{head_slug}' not found, skipping")
                    continue
                QuestionDoctrineHead.objects.update_or_create(
                    question=question,
                    doctrine_head=head,
                )
                head_link_count += 1

        mark_data_current(version_key, data_path)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(loci)} ontology loci, {len(attributes)} attributes, "
            f"{len(heads)} heads, {tag_count} question tags, and "
            f"{head_link_count} head links"
        ))
