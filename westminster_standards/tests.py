"""Data invariant tests for the westminster_standards app.

Run with:

    python manage.py test westminster_standards

These tests catch the kinds of drift that aren't caught by Django's
``manage.py check``: persona ``attrs`` keys that don't exist in the
ontology, crux ``persona_slugs`` that reference deleted personas, crux
``attribute_keys`` that have been renamed in the ontology, duplicate
slugs, baseline values that aren't valid option labels.

They run quickly (one pass over the in-memory data) and serve as a
canary when any layer is edited.
"""

import re

from django.test import SimpleTestCase, TestCase

from .data import DIMENSIONS, WESTMINSTER_BASELINE_ATTRS, ATTR_VALUE_KEYS
from .personas import PERSONAS, get_persona_by_slug
from .cruxes import CRUXES
from .works import WORKS, get_work_by_slug


class OntologyInvariants(SimpleTestCase):
    """The ontology itself must be internally consistent."""

    def test_attribute_count(self):
        n = sum(len(d['attributes']) for d in DIMENSIONS)
        self.assertEqual(n, 35,
                         f"expected 35 attributes total, got {n}")

    def test_baseline_covers_every_attribute(self):
        expected = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                expected.add(f"{d['key']}_{a['key']}")
        self.assertEqual(set(WESTMINSTER_BASELINE_ATTRS.keys()), expected,
                         "WESTMINSTER_BASELINE_ATTRS must have an entry for "
                         "every (locus, attribute) pair")

    def test_baseline_values_are_real(self):
        for full_key, label in WESTMINSTER_BASELINE_ATTRS.items():
            self.assertIn((full_key, label), ATTR_VALUE_KEYS,
                          f"WESTMINSTER_BASELINE_ATTRS[{full_key!r}] = "
                          f"{label!r} is not a known value label")

    def test_value_keys_unique_within_attribute(self):
        for d in DIMENSIONS:
            for a in d['attributes']:
                keys = [v['key'] for v in a['values']]
                self.assertEqual(len(keys), len(set(keys)),
                                 f"duplicate value keys on {d['key']}_{a['key']}")


class PersonaInvariants(SimpleTestCase):
    """Every persona must have valid slug, attrs, and overrides."""

    def test_slugs_unique(self):
        slugs = [p['slug'] for p in PERSONAS]
        self.assertEqual(len(slugs), len(set(slugs)),
                         "duplicate persona slugs")

    def test_required_fields(self):
        required = ['slug', 'number', 'name', 'dates', 'role',
                    'tagline', 'bio', 'attrs']
        for p in PERSONAS:
            for field in required:
                self.assertIn(field, p, f"{p.get('slug')} missing {field}")

    def test_attrs_keys_are_real(self):
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        for p in PERSONAS:
            for k in p.get('attrs', {}).keys():
                self.assertIn(k, ontology_keys,
                              f"{p['slug']} has attrs[{k!r}] which is not "
                              f"a known ontology attribute")

    def test_attrs_values_are_real(self):
        for p in PERSONAS:
            for full_key, label in p['attrs'].items():
                self.assertIn((full_key, label), ATTR_VALUE_KEYS,
                              f"{p['slug']}: attrs[{full_key!r}] = "
                              f"{label!r} is not a known value label")


class CruxInvariants(SimpleTestCase):
    """Every crux must have valid slug, locus, attributes, and party refs."""

    def test_slugs_unique(self):
        slugs = [c['slug'] for c in CRUXES]
        self.assertEqual(len(slugs), len(set(slugs)),
                         "duplicate crux slugs")

    def test_locus_keys_are_real(self):
        dim_keys = {d['key'] for d in DIMENSIONS}
        for c in CRUXES:
            self.assertIn(c['locus_key'], dim_keys,
                          f"{c['slug']}: locus_key {c['locus_key']!r} "
                          f"is not a known ontology locus")

    def test_attribute_keys_are_real(self):
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        for c in CRUXES:
            for k in c.get('attribute_keys', []):
                self.assertIn(k, ontology_keys,
                              f"{c['slug']}: attribute_keys contains "
                              f"{k!r} which is not a known attribute")

    def test_persona_slugs_exist(self):
        for c in CRUXES:
            for party in c.get('parties', []):
                for slug in party.get('persona_slugs', []):
                    self.assertIsNotNone(get_persona_by_slug(slug),
                                         f"{c['slug']}: party "
                                         f"{party.get('name')!r} references "
                                         f"unknown persona {slug!r}")

    def test_outcome_is_known(self):
        known = {'settled-clear', 'settled-with-latitude',
                 'rejected-alternative', 'deferred', 'mixed'}
        for c in CRUXES:
            self.assertIn(c.get('outcome'), known,
                          f"{c['slug']}: unknown outcome {c.get('outcome')!r}")


class WorksInvariants(SimpleTestCase):
    """The loaded WCF / LC / SC must be structurally complete."""

    def test_three_canonical_works_present(self):
        for slug in ('wcf', 'wlc', 'wsc'):
            self.assertIsNotNone(get_work_by_slug(slug),
                                 f"work {slug!r} missing")

    def test_wcf_has_33_chapters(self):
        wcf = get_work_by_slug('wcf')
        self.assertIsNotNone(wcf['chapters'])
        self.assertEqual(len(wcf['chapters']), 33)

    def test_wlc_has_196_questions(self):
        wlc = get_work_by_slug('wlc')
        self.assertIsNotNone(wlc['questions'])
        self.assertEqual(len(wlc['questions']), 196)

    def test_wsc_has_107_questions(self):
        wsc = get_work_by_slug('wsc')
        self.assertIsNotNone(wsc['questions'])
        self.assertEqual(len(wsc['questions']), 107)

    def test_chapter_numbers_contiguous(self):
        wcf = get_work_by_slug('wcf')
        numbers = [ch['number'] for ch in wcf['chapters']]
        self.assertEqual(numbers, list(range(1, 34)))

    def test_catechism_question_numbers_contiguous(self):
        for slug, n in (('wlc', 196), ('wsc', 107)):
            cat = get_work_by_slug(slug)
            numbers = [q['number'] for q in cat['questions']]
            self.assertEqual(numbers, list(range(1, n + 1)))

    def test_shorter_catechism_has_proof_texts(self):
        # Every Shorter-Catechism question carries the Assembly's proof
        # texts (annexed 1648); each proof has a clause Id and references,
        # and each reference is {'ref': str, 'verses': [...]}.
        wsc = get_work_by_slug('wsc')
        for q in wsc['questions']:
            proofs = q.get('proofs')
            self.assertTrue(proofs, f"WSC Q.{q['number']} has no proof texts")
            for proof in proofs:
                self.assertIn('Id', proof)
                self.assertTrue(proof.get('References'),
                                f"WSC Q.{q['number']} proof {proof.get('Id')} "
                                "has no references")
                for r in proof['References']:
                    self.assertIn('ref', r)
                    self.assertIn('verses', r)

    def test_proof_verses_resolve_for_most_references(self):
        # The KJV verse text should be attached to the large majority of
        # proof references in both catechisms.
        for slug in ('wsc', 'wlc'):
            total = with_text = 0
            for q in get_work_by_slug(slug)['questions']:
                for proof in q.get('proofs', []):
                    for r in proof['References']:
                        total += 1
                        if r['verses']:
                            with_text += 1
            self.assertGreater(with_text / total, 0.9,
                               f"{slug}: only {with_text}/{total} refs have verse text")


class SchoolInvariants(SimpleTestCase):
    """Every school must have valid slug, attrs, and anchor refs."""

    def test_slugs_unique(self):
        from .schools import SCHOOLS
        slugs = [s['slug'] for s in SCHOOLS]
        self.assertEqual(len(slugs), len(set(slugs)),
                         "duplicate school slugs")

    def test_attrs_values_are_real(self):
        from .schools import SCHOOLS
        for s in SCHOOLS:
            for full_key, label in s['attrs'].items():
                self.assertIn((full_key, label), ATTR_VALUE_KEYS,
                              f"{s['slug']}: attrs[{full_key!r}] = "
                              f"{label!r} is not a known value label")

    def test_anchor_persona_slugs_exist(self):
        from .schools import SCHOOLS
        for s in SCHOOLS:
            for slug in s.get('anchor_persona_slugs', []):
                self.assertIsNotNone(get_persona_by_slug(slug),
                                     f"{s['slug']}: anchor persona "
                                     f"{slug!r} does not exist")

    def test_period_is_known(self):
        from .schools import SCHOOLS
        known = {'assembly-party', 'receiving-tradition'}
        for s in SCHOOLS:
            self.assertIn(s.get('period'), known,
                          f"{s['slug']}: unknown period {s.get('period')!r}")


class HeadsOfDoctrineInvariants(SimpleTestCase):
    """Every head of doctrine must have valid slug, locus, and references."""

    def test_slugs_unique(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        slugs = [h['slug'] for h in HEADS_OF_DOCTRINE]
        self.assertEqual(len(slugs), len(set(slugs)),
                         "duplicate head slugs")

    def test_all_wcf_section_references_exist(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        wcf = get_work_by_slug('wcf')
        self.assertIsNotNone(wcf)
        # Build a set of valid (chapter, section) pairs.
        valid = set()
        for ch in wcf['chapters']:
            for s in ch['sections']:
                valid.add((ch['number'], s['number']))
        for h in HEADS_OF_DOCTRINE:
            for cs in h['wcf_sections']:
                self.assertIn(tuple(cs), valid,
                              f"{h['slug']}: WCF section {cs} does not exist")

    def test_all_wsc_question_references_in_range(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        wsc = get_work_by_slug('wsc')
        self.assertIsNotNone(wsc)
        valid = {q['number'] for q in wsc['questions']}
        for h in HEADS_OF_DOCTRINE:
            for q in h['wsc_questions']:
                self.assertIn(q, valid,
                              f"{h['slug']}: WSC Q. {q} out of range")

    def test_all_wlc_question_references_in_range(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        wlc = get_work_by_slug('wlc')
        self.assertIsNotNone(wlc)
        valid = {q['number'] for q in wlc['questions']}
        for h in HEADS_OF_DOCTRINE:
            for q in h['wlc_questions']:
                self.assertIn(q, valid,
                              f"{h['slug']}: WLC Q. {q} out of range")

    def test_all_crux_slug_references_exist(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        from .cruxes import CRUXES
        valid = {c['slug'] for c in CRUXES}
        for h in HEADS_OF_DOCTRINE:
            for cs in h['related_crux_slugs']:
                self.assertIn(cs, valid,
                              f"{h['slug']}: crux slug {cs!r} does not exist")

    def test_all_locus_keys_are_valid(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        dim_keys = {d['key'] for d in DIMENSIONS}
        for h in HEADS_OF_DOCTRINE:
            self.assertIn(h['locus_key'], dim_keys,
                          f"{h['slug']}: locus_key {h['locus_key']!r} "
                          f"is not a known ontology locus")

    def test_all_attribute_keys_are_real(self):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        for h in HEADS_OF_DOCTRINE:
            keys = h.get('attribute_keys', [])
            self.assertTrue(keys,
                            f"{h['slug']}: has no attribute_keys")
            self.assertEqual(len(keys), len(set(keys)),
                             f"{h['slug']}: duplicate attribute_keys")
            for k in keys:
                self.assertIn(k, ontology_keys,
                              f"{h['slug']}: attribute_keys contains {k!r} "
                              f"which is not a known ontology attribute")


class SectionOntologyTags(SimpleTestCase):
    """The ontology tags derived for work-sections (union of the covering
    heads' attribute_keys) must always resolve to real ontology attributes,
    and the WCF — every section of which is covered by a head — should be
    well tagged."""

    def test_wcf_section_attributes_are_real(self):
        from .heads_of_doctrine import attributes_for_wcf_section
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        wcf = get_work_by_slug('wcf')
        tagged_sections = 0
        for ch in wcf['chapters']:
            for s in ch['sections']:
                keys = attributes_for_wcf_section(ch['number'], s['number'])
                self.assertEqual(len(keys), len(set(keys)),
                                 f"WCF {ch['number']}.{s['number']}: "
                                 f"duplicate ontology tags")
                for k in keys:
                    self.assertIn(k, ontology_keys,
                                  f"WCF {ch['number']}.{s['number']}: "
                                  f"unknown ontology attribute {k!r}")
                if keys:
                    tagged_sections += 1
                else:
                    self.fail(f"WCF {ch['number']}.{s['number']} has no "
                              f"ontology tag")
        self.assertGreater(tagged_sections, 0)

    def test_every_catechism_question_has_a_head(self):
        from .heads_of_doctrine import heads_for_catechism_question
        for slug in ('wsc', 'wlc'):
            work = get_work_by_slug(slug)
            uncovered = [q['number'] for q in work['questions']
                         if not heads_for_catechism_question(slug, q['number'])]
            self.assertEqual(uncovered, [],
                             f"{slug} questions with no head of doctrine: "
                             f"{uncovered}")

    def test_representative_flag_distinguishes_core_and_nearest_fit(self):
        from .heads_of_doctrine import (
            attribute_tags_for_wcf_section, _REPRESENTATIVE_ATTRS)
        # Sanity: the representative pairs reference real heads/attributes.
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        head_slugs = {h['slug'] for h in HEADS_OF_DOCTRINE}
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        for slug, key in _REPRESENTATIVE_ATTRS:
            self.assertIn(slug, head_slugs)
            self.assertIn(key, ontology_keys)
        # Providence (WCF 5) is tagged representatively; the eternal decree
        # (WCF 3) holds the same attribute as a core/contested axis.
        prov = attribute_tags_for_wcf_section(5, 1)
        self.assertTrue(any(t['key'] == 'god_decree_order_of_decrees'
                            and t['representative'] for t in prov))
        decree = attribute_tags_for_wcf_section(3, 3)
        self.assertTrue(any(t['key'] == 'god_decree_order_of_decrees'
                            and not t['representative'] for t in decree))

    def test_catechism_question_attributes_are_real(self):
        from .heads_of_doctrine import attributes_for_catechism_question
        ontology_keys = set()
        for d in DIMENSIONS:
            for a in d['attributes']:
                ontology_keys.add(f"{d['key']}_{a['key']}")
        for slug in ('wsc', 'wlc'):
            work = get_work_by_slug(slug)
            for q in work['questions']:
                keys = attributes_for_catechism_question(slug, q['number'])
                self.assertTrue(keys,
                                f"{slug} Q.{q['number']} has no ontology tag")
                for k in keys:
                    self.assertIn(k, ontology_keys,
                                  f"{slug} Q.{q['number']}: unknown "
                                  f"ontology attribute {k!r}")


class CrossLinkInvariants(SimpleTestCase):
    """Cruxes that quote confessional language should resolve into the
    loaded text — i.e. the citation parser should find at least one
    valid reference for cruxes whose ``language`` field is non-empty."""

    def test_citation_parser_resolves_some_cruxes(self):
        from .citations import find_citations
        cruxes_with_language = [c for c in CRUXES if c.get('language')]
        cruxes_with_resolved_citations = 0
        for c in cruxes_with_language:
            sources = [c.get('language', '')] + list(c.get('references', []))
            for src in sources:
                if any(find_citations(src)):
                    cruxes_with_resolved_citations += 1
                    break
        # We expect at least 25 of the 30 cruxes to have resolvable citations.
        self.assertGreaterEqual(cruxes_with_resolved_citations, 25,
                                f"only {cruxes_with_resolved_citations} of "
                                f"{len(cruxes_with_language)} cruxes have "
                                f"resolvable citations in language/references")


class PersonaOntologyLinks(TestCase):
    """A persona's positions should be explorable, especially where he
    departs from the Confession.

    Every value on a persona page names a position that has its own page
    explaining what it is, who else held it, and what it was argued against —
    but the persona page rendered them as plain text, so the one genuinely
    interesting fact about a divine (that he disagreed with Westminster here)
    was a dead end. The school and comparison pages already linked theirs.
    """

    def _persona_with_an_override(self):
        for persona in PERSONAS:
            for key, value in persona['attrs'].items():
                if WESTMINSTER_BASELINE_ATTRS.get(key) not in (None, value):
                    return persona, key
        self.fail('no persona departs from the baseline')

    def test_a_departure_links_to_the_position_it_takes(self):
        persona, _key = self._persona_with_an_override()
        body = self.client.get(
            f"/atlas/personas/{persona['slug']}/"
        ).content.decode()
        self.assertIn('/atlas/dimension/', body)
        self.assertIn('ws-la-override', body)

    def test_a_departure_names_what_it_departs_from(self):
        persona, _key = self._persona_with_an_override()
        body = self.client.get(
            f"/atlas/personas/{persona['slug']}/"
        ).content.decode()
        # The Westminster position is stated inline, not left to a hover.
        self.assertIn('ws-la-baseline', body)
        self.assertIn('departs from the Westminster position', body)

    def test_arrowsmiths_atonement_position_is_clickable(self):
        """The case that prompted this: John Arrowsmith is a hypothetical
        universalist, which is precisely where he parts from the Confession."""
        body = self.client.get('/atlas/personas/john-arrowsmith/').content.decode()
        self.assertIn(
            '/atlas/dimension/god_decree/extent_of_atonement/hypothetical_universal/',
            body,
        )
        # ...and the Confession's own position is linked beside it.
        self.assertIn(
            '/atlas/dimension/god_decree/extent_of_atonement/particular/', body,
        )

    def test_every_linked_value_page_resolves(self):
        persona, _key = self._persona_with_an_override()
        body = self.client.get(f"/atlas/personas/{persona['slug']}/").content.decode()
        hrefs = set(re.findall(r'href="(/atlas/dimension/[^"]+)"', body))
        self.assertTrue(hrefs)
        for href in sorted(hrefs):
            self.assertEqual(
                self.client.get(href).status_code, 200, f'{href} does not resolve',
            )


class PositionGlossing(TestCase):
    """The 117 positions all carry a definition that nothing used to render."""

    def test_a_position_renders_as_a_link_carrying_its_definition(self):
        from .templatetags.atlas_tags import position

        html = position('Hypothetical-Universal', 'god_decree', 'extent_of_atonement')
        self.assertIn('/atlas/dimension/god_decree/extent_of_atonement/'
                      'hypothetical_universal/', html)
        self.assertIn('title="', html)

    def test_a_position_resolves_from_a_unique_label_alone(self):
        """Some templates hold only the label, not the keys."""
        from .templatetags.atlas_tags import position

        self.assertIn('/atlas/dimension/', position('Supralapsarian'))

    def test_an_unknown_position_degrades_to_plain_text(self):
        from .templatetags.atlas_tags import position

        self.assertEqual(position('Not-A-Position', 'x', 'y'), 'Not-A-Position')

    def test_every_position_in_the_ontology_can_be_glossed(self):
        from .glossary import VALUE_BY_KEYS

        self.assertEqual(len(VALUE_BY_KEYS), 117)
        undefined = [
            entry['label'] for entry in VALUE_BY_KEYS.values()
            if not entry['definition']
        ]
        self.assertEqual(undefined, [])

    def test_intersection_pages_link_their_positions(self):
        """These pages listed 15+ hyphenated positions as flat text."""
        body = self.client.get('/atlas/dimensions/scripture-god_decree/').content.decode()
        self.assertIn('/atlas/dimension/scripture/', body)
        self.assertIn('/atlas/dimension/god_decree/', body)


class ProseCrossLinks(TestCase):
    """Divines named in a biography or a role blurb should be reachable."""

    def test_divines_named_in_prose_are_linked(self):
        from .templatetags.atlas_tags import link_divines

        html = link_divines('Alexander Henderson and George Gillespie argued the case.')
        self.assertIn('/atlas/personas/alexander-henderson/', html)
        self.assertIn('/atlas/personas/george-gillespie/', html)

    def test_a_persona_is_not_linked_to_his_own_page(self):
        from .templatetags.atlas_tags import link_divines

        html = link_divines('Samuel Rutherford wrote Lex Rex.', 'samuel-rutherford')
        self.assertNotIn('/atlas/personas/samuel-rutherford/', html)

    def test_prose_cannot_smuggle_markup(self):
        from .templatetags.atlas_tags import link_divines

        html = link_divines('<script>alert(1)</script> said George Gillespie.')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_the_role_blurb_on_a_persona_page_is_linked(self):
        body = self.client.get('/atlas/personas/samuel-rutherford/').content.decode()
        self.assertIn('/atlas/personas/george-gillespie/', body)


class DeparturesInTheHeader(TestCase):
    """Where a divine broke with the Confession was buried in a collapsed
    section; it is the most interesting thing about him."""

    def test_a_departure_is_stated_in_the_header(self):
        body = self.client.get('/atlas/personas/john-arrowsmith/').content.decode()
        self.assertIn('Departs from the Confession on', body)
        self.assertIn('Hypothetical-Universal', body)
        self.assertIn('Particular', body)

    def test_a_persona_holding_the_baseline_says_so(self):
        from .personas import PERSONAS
        from .data import WESTMINSTER_BASELINE_ATTRS

        plain = next(
            p for p in PERSONAS
            if all(WESTMINSTER_BASELINE_ATTRS.get(k) == v for k, v in p['attrs'].items())
        )
        body = self.client.get(f"/atlas/personas/{plain['slug']}/").content.decode()
        self.assertIn('Holds the Westminster position', body)


class FacetedBrowse(TestCase):
    """The value pages answer "who held this?" one position at a time; the
    persona list should answer it for any position, and for the more useful
    question of who departed from the Confession at all."""

    def test_filtering_by_a_position_narrows_the_list(self):
        resp = self.client.get('/atlas/personas/', {
            'attr': 'god_decree_extent_of_atonement',
            'value': 'Hypothetical-Universal',
        })
        assert resp.status_code == 200
        self.assertLess(resp.context['shown'], resp.context['total'])
        for persona in resp.context['personas_flat']:
            self.assertEqual(
                persona['attrs']['god_decree_extent_of_atonement'],
                'Hypothetical-Universal',
            )

    def test_filtering_to_those_who_depart_from_the_confession(self):
        from .data import WESTMINSTER_BASELINE_ATTRS

        resp = self.client.get('/atlas/personas/', {'departures': '1'})
        self.assertLess(resp.context['shown'], resp.context['total'])
        for persona in resp.context['personas_flat']:
            self.assertTrue(any(
                WESTMINSTER_BASELINE_ATTRS.get(key) != value
                for key, value in persona['attrs'].items()
            ), f"{persona['slug']} holds the baseline throughout")

    def test_an_unrecognised_facet_is_ignored_rather_than_erroring(self):
        resp = self.client.get('/atlas/personas/', {'attr': 'nonsense', 'value': 'x'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['facet']['active'])
        self.assertEqual(resp.context['shown'], resp.context['total'])

    def test_no_facet_shows_everyone(self):
        resp = self.client.get('/atlas/personas/')
        self.assertEqual(resp.context['shown'], resp.context['total'])
