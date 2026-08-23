"""Views for the Westminster Standards atlas.

The ontology and dimension pages are the scaffold-time deliverables;
the persona/work/school/question/controversy/case pages will come
online as those layer files are populated.
"""

import re

from django.shortcuts import render
from django.http import Http404
from django.utils.html import escape, mark_safe

from .data import (
    DIMENSIONS, MATRIX_ATTRIBUTES,
    DIMENSION_PAIRS, DIMENSION_TRIPLETS,
    DIMENSION_QUADRUPLETS, DIMENSION_QUINTUPLETS, ALL_EIGHT,
    WESTMINSTER_BASELINE_ATTRS, ATTR_LABELS,
)
from .personas import PERSONAS, get_persona_by_slug, role_context
from .cruxes import CRUXES, get_crux_by_slug, cruxes_by_locus, cruxes_for_persona
from .schools import SCHOOLS, get_school_by_slug
from .works import (
    WORKS, get_work_by_slug, get_wcf_chapter, get_catechism_question,
)
from .citations import (
    linkify as linkify_citations,
    cruxes_for_wcf_chapter,
    cruxes_for_catechism_question,
    schools_mentioned_in_legacy,
)
from .locus_mapping import (
    wcf_chapter_loci, catechism_question_loci,
    wcf_chapters_for_locus, catechism_questions_for_locus,
    directory_sections_for_locus, directory_section_loci,
)
from .heads_of_doctrine import (
    HEADS_OF_DOCTRINE, get_head_by_slug, heads_by_locus,
    heads_for_wcf_section, heads_for_catechism_question,
    heads_for_crux,
    attribute_tags_for_wcf_section, attribute_tags_for_catechism_question,
    attribute_tags_for_heads,
)
from .works import WORKS
from .schools import SCHOOLS
from .questions import QUESTIONS
from .controversies import CONTROVERSIES
from .cases import CASES


def _counts():
    return {
        'personas': len(PERSONAS),
        'works': len(WORKS),
        'schools': len(SCHOOLS),
        'questions': len(QUESTIONS),
        'controversies': len(CONTROVERSIES),
        'cases': len(CASES),
        'cruxes': len(CRUXES),
        'heads': len(HEADS_OF_DOCTRINE),
        'dimensions': len(DIMENSIONS),
        'attributes': sum(len(d['attributes']) for d in DIMENSIONS),
    }


def _compact_range(numbers):
    """Turn [1,2,3,5,6,8] into '1–3, 5–6, 8' for display."""
    if not numbers:
        return ''
    nums = sorted(numbers)
    ranges = []
    start = end = nums[0]
    for n in nums[1:]:
        if n == end + 1:
            end = n
        else:
            ranges.append(f'{start}–{end}' if end > start else str(start))
            start = end = n
    ranges.append(f'{start}–{end}' if end > start else str(start))
    return ', '.join(ranges)


def _dimension_by_key(key):
    for d in DIMENSIONS:
        if d['key'] == key:
            return d
    return None


def _resolve_attr_rows(items):
    """Resolve ontology attributes into display rows: the locus, the
    attribute, its short key, and the Westminster baseline value (so each
    value can link to its value page).

    Each item is either a bare full key (e.g. 'god_decree_reprobation') or a
    tag dict {'key', 'representative'}; the resulting row carries a
    ``representative`` flag so the UI can mark nearest-fit tags.
    """
    rows = []
    for item in items:
        if isinstance(item, dict):
            full_key = item['key']
            representative = item.get('representative', False)
        else:
            full_key = item
            representative = False
        for d in DIMENSIONS:
            prefix = d['key'] + '_'
            if not full_key.startswith(prefix):
                continue
            short_attr_key = full_key[len(prefix):]
            attr = next((a for a in d['attributes']
                         if a['key'] == short_attr_key), None)
            if attr:
                baseline_label = WESTMINSTER_BASELINE_ATTRS.get(full_key)
                baseline_value_key = None
                if baseline_label:
                    bv = next((v for v in attr['values']
                               if v['label'] == baseline_label), None)
                    if bv:
                        baseline_value_key = bv['key']
                rows.append({
                    'dim': d,
                    'attr': attr,
                    'short_attr_key': short_attr_key,
                    'baseline_label': baseline_label,
                    'baseline_value_key': baseline_value_key,
                    'representative': representative,
                })
            break
    return rows


def home(request):
    return render(request, 'westminster_standards/home.html', {
        'counts': _counts(),
        'dimensions': DIMENSIONS,
        'daily_text': _pick_daily_text(),
    })


def _pick_daily_text():
    """Pick a Shorter Catechism Q&A or a brief WCF section as the
    home-page text-of-the-day. Seeded by today's date so the choice is
    stable for a 24-hour window.
    """
    import random
    from datetime import date

    rnd = random.Random(date.today().toordinal())

    # Build a small pool of suitable short selections. The Shorter
    # Catechism is well-suited; some short, self-contained WCF sections
    # also work; longer sections / long LC answers would not fit.
    candidates = []

    wsc = get_work_by_slug('wsc')
    if wsc:
        for q in wsc.get('questions') or []:
            candidates.append({
                'kind': 'wsc',
                'q': q,
                'url': f"/westminster_standards/works/wsc/q/{q['number']}/",
                'reference': f"Shorter Catechism Q. {q['number']}",
            })

    wcf = get_work_by_slug('wcf')
    if wcf:
        for ch in wcf.get('chapters') or []:
            for s in ch.get('sections') or []:
                if 200 <= len(s['content']) <= 700:
                    candidates.append({
                        'kind': 'wcf_section',
                        'section': s,
                        'chapter': ch,
                        'url': f"/westminster_standards/works/wcf/chapter/{ch['number']}/#s{s['number']}",
                        'reference': f"WCF {ch['roman']}.{s['number']} · {ch['title']}",
                    })

    if not candidates:
        return None
    return rnd.choice(candidates)


def ontology(request):
    attr_count = sum(len(d.get('attributes', [])) for d in DIMENSIONS)
    annotated_dimensions = []
    for dim in DIMENSIONS:
        attrs = []
        for attr in dim['attributes']:
            full_key = f"{dim['key']}_{attr['key']}"
            baseline_label = WESTMINSTER_BASELINE_ATTRS.get(full_key)
            baseline_value = None
            alternatives = []
            for v in attr['values']:
                display_label = v['label'].replace('-', ' ')
                entry = {
                    'value': v,
                    'display_label': display_label,
                    'is_baseline': v['label'] == baseline_label,
                }
                if entry['is_baseline']:
                    baseline_value = entry
                else:
                    alternatives.append(entry)
            attrs.append({
                'attr': attr,
                'baseline': baseline_value,
                'alternatives': alternatives,
                'total_values': len(attr['values']),
            })
        # Context counts for this locus
        wcf_chs = wcf_chapters_for_locus(dim['key'])
        wsc_qs = catechism_questions_for_locus('wsc', dim['key'])
        wlc_qs = catechism_questions_for_locus('wlc', dim['key'])
        locus_cruxes = cruxes_by_locus(dim['key'])
        dpw_secs = directory_sections_for_locus('dpw', dim['key'])
        fpcg_secs = directory_sections_for_locus('fpcg', dim['key'])
        ssk_secs = directory_sections_for_locus('ssk', dim['key'])
        annotated_dimensions.append({
            'dim': dim,
            'attrs': attrs,
            'wcf_count': len(wcf_chs),
            'wsc_count': len(wsc_qs),
            'wlc_count': len(wlc_qs),
            'crux_count': len(locus_cruxes),
            'dpw_count': len(dpw_secs),
            'fpcg_count': len(fpcg_secs),
            'ssk_count': len(ssk_secs),
        })
    return render(request, 'westminster_standards/ontology.html', {
        'annotated_dimensions': annotated_dimensions,
        'counts': _counts(),
        'attr_count': attr_count,
    })


def dimension_detail(request, dim_key):
    dim = _dimension_by_key(dim_key)
    if not dim:
        raise Http404
    rows = []
    for attr in dim['attributes']:
        full_key = f"{dim['key']}_{attr['key']}"
        baseline_label = WESTMINSTER_BASELINE_ATTRS.get(full_key)
        rows.append({
            'attr': attr,
            'full_key': full_key,
            'baseline_label': baseline_label,
        })
    # WCF chapters and catechism questions that fall under this locus.
    wcf = get_work_by_slug('wcf')
    wcf_ch_nums = wcf_chapters_for_locus(dim_key)
    wcf_chs = []
    if wcf and wcf.get('chapters'):
        for ch in wcf['chapters']:
            if ch['number'] in wcf_ch_nums:
                wcf_chs.append(ch)
    wsc_q_nums = catechism_questions_for_locus('wsc', dim_key)
    wlc_q_nums = catechism_questions_for_locus('wlc', dim_key)

    # DPW/FPCG/SSK sections under this locus
    dir_works = []
    for dir_slug, dir_label in [('dpw', 'Directory for Public Worship'),
                                 ('fpcg', 'Form of Church Government'),
                                 ('ssk', 'Sum of Saving Knowledge')]:
        sec_nums = directory_sections_for_locus(dir_slug, dim_key)
        if sec_nums:
            work = get_work_by_slug(dir_slug)
            if work and work.get('chapters'):
                secs = [s for s in work['chapters'] if s['number'] in sec_nums]
                dir_works.append({
                    'slug': dir_slug,
                    'label': dir_label,
                    'short_title': work['short_title'],
                    'sections': secs,
                })

    return render(request, 'westminster_standards/dimension_detail.html', {
        'dim': dim,
        'rows': rows,
        'wcf_chapters': wcf_chs,
        'wsc_question_range': _compact_range(wsc_q_nums),
        'wsc_question_count': len(wsc_q_nums),
        'wlc_question_range': _compact_range(wlc_q_nums),
        'wlc_question_count': len(wlc_q_nums),
        'wsc_first_q': wsc_q_nums[0] if wsc_q_nums else None,
        'wlc_first_q': wlc_q_nums[0] if wlc_q_nums else None,
        'dir_works': dir_works,
        'counts': _counts(),
        'dimensions': DIMENSIONS,
    })


def personas_list(request):
    """Listing of all Westminster personas, grouped by role.

    Roles are heterogeneous strings (e.g. 'English Presbyterian minister',
    'Scottish Commissioner (minister)'); we group by the first segment
    before any parenthesis and preserve a stable ordering.
    """
    GROUP_ORDER = [
        'Prolocutor (1643–1646)',
        'Prolocutor (1646–1652)',
        'First Assessor',
        'Second Assessor',
        'Scribe',
        'Scottish Commissioner (minister)',
        'Scottish Commissioner (ruling elder)',
        'English Presbyterian minister',
        'English Presbyterian minister (expelled)',
        'Independent / Dissenting Brother',
        'Independent minister',
        'Erastian minister',
        'Lay Assessor (Commons)',
        'Lay Assessor (Lords)',
        'Scottish-born irenicist; superadded',
        'Independent army chaplain; superadded',
        'Independent army chaplain',
        'Originally named — declined (royalist)',
        'Originally named — minimal attendance',
        'Originally named — minimal attendance (royalist sympathy)',
        'Lay Assessor (Commons) — d. June 1643',
        'Lay Assessor (Lords) — d. May 1641',
    ]
    by_role = {}
    for p in PERSONAS:
        by_role.setdefault(p['role'], []).append(p)
    # Stable display order: known roles first (in GROUP_ORDER), then any
    # remaining roles alphabetically.
    seen = set(GROUP_ORDER)
    groups = []
    for role in GROUP_ORDER:
        if role in by_role:
            groups.append({'role': role, 'people': by_role[role]})
    for role in sorted(by_role.keys()):
        if role in seen:
            continue
        groups.append({'role': role, 'people': by_role[role]})
    personas_flat = sorted(PERSONAS, key=lambda p: p['name'].lower())
    return render(request, 'westminster_standards/personas_list.html', {
        'groups': groups,
        'personas_flat': personas_flat,
        'total': len(PERSONAS),
        'counts': _counts(),
    })


def persona_detail(request, slug):
    p = get_persona_by_slug(slug)
    if not p:
        raise Http404
    # Group the persona's attrs by dimension for display.
    by_dim = []
    overrides = set()  # full_attr_keys where the value differs from baseline
    for dim in DIMENSIONS:
        rows = []
        for attr in dim['attributes']:
            full_key = f"{dim['key']}_{attr['key']}"
            label = p['attrs'].get(full_key)
            baseline_label = WESTMINSTER_BASELINE_ATTRS.get(full_key)
            is_override = label != baseline_label
            if is_override:
                overrides.add(full_key)
            value_key = None
            value_def = None
            baseline_key = None
            for v in attr['values']:
                if v['label'] == label:
                    value_key = v['key']
                    value_def = v.get('definition')
                if v['label'] == baseline_label:
                    baseline_key = v['key']
            rows.append({
                'attr': attr,
                'dim_key': dim['key'],
                'value_label': label,
                'value_key': value_key,
                'value_definition': value_def,
                'is_override': is_override,
                'baseline_label': baseline_label,
                'baseline_key': baseline_key,
            })
        by_dim.append({'dim': dim, 'rows': rows})

    # The one genuinely interesting fact about a divine is where he parted
    # from the Confession; it belongs in the header, not two clicks down.
    departures = [
        {
            'dim_key': dim_entry['dim']['key'],
            'attr_key': row['attr']['key'],
            'attr_label': row['attr']['label'],
            'value_label': row['value_label'],
            'baseline_label': row['baseline_label'],
        }
        for dim_entry in by_dim
        for row in dim_entry['rows']
        if row['is_override']
    ]
    crux_appearances = cruxes_for_persona(slug)
    persona_schools = [s for s in SCHOOLS if slug in s.get('anchor_persona_slugs', [])]
    return render(request, 'westminster_standards/persona_detail.html', {
        'p': p,
        'by_dim': by_dim,
        'departures': departures,
        'override_count': len(overrides),
        'crux_appearances': crux_appearances,
        'persona_schools': persona_schools,
        'role_context': role_context(p.get('role')),
        'counts': _counts(),
    })


_OUTCOME_LABELS = {
    'settled-clear': 'Settled clearly',
    'settled-with-latitude': 'Settled with deliberate latitude',
    'rejected-alternative': 'Alternative rejected',
    'deferred': 'Deferred',
    'mixed': 'Mixed',
}


def compare_personas(request):
    def _persona_from_query(key):
        raw = (request.GET.get(key) or request.GET.get(f'{key}_text') or '').strip()
        if not raw:
            return None
        direct = get_persona_by_slug(raw)
        if direct:
            return direct
        for persona in PERSONAS:
            label = f"{persona['name']} ({persona['dates']})"
            if raw == persona['name'] or raw == label:
                return persona
        return None

    p_a = _persona_from_query('a')
    p_b = _persona_from_query('b')

    comparison = None
    if p_a and p_b:
        rows = []
        diffs = 0
        for dim in DIMENSIONS:
            dim_rows = []
            for attr in dim['attributes']:
                full_key = f"{dim['key']}_{attr['key']}"
                val_a = p_a['attrs'].get(full_key, '')
                val_b = p_b['attrs'].get(full_key, '')
                baseline = WESTMINSTER_BASELINE_ATTRS.get(full_key, '')
                is_diff = val_a != val_b
                if is_diff:
                    diffs += 1
                # Resolve value keys for linking
                def _vkey(label):
                    for v in attr['values']:
                        if v['label'] == label:
                            return v['key']
                    return None
                dim_rows.append({
                    'attr': attr,
                    'dim_key': dim['key'],
                    'val_a': val_a,
                    'val_b': val_b,
                    'vkey_a': _vkey(val_a),
                    'vkey_b': _vkey(val_b),
                    'baseline': baseline,
                    'is_diff': is_diff,
                    'a_is_baseline': val_a == baseline,
                    'b_is_baseline': val_b == baseline,
                })
            rows.append({'dim': dim, 'attrs': dim_rows})
        comparison = {'rows': rows, 'diffs': diffs}

    return render(request, 'westminster_standards/compare_personas.html', {
        'personas': sorted(PERSONAS, key=lambda p: p['name']),
        'p_a': p_a,
        'p_b': p_b,
        'comparison': comparison,
        'counts': _counts(),
    })


def compare_schools(request):
    slug_a = request.GET.get('a', '')
    slug_b = request.GET.get('b', '')
    s_a = get_school_by_slug(slug_a) if slug_a else None
    s_b = get_school_by_slug(slug_b) if slug_b else None

    comparison = None
    if s_a and s_b:
        rows = []
        diffs = 0
        for dim in DIMENSIONS:
            dim_rows = []
            for attr in dim['attributes']:
                full_key = f"{dim['key']}_{attr['key']}"
                val_a = s_a['attrs'].get(full_key, '')
                val_b = s_b['attrs'].get(full_key, '')
                baseline = WESTMINSTER_BASELINE_ATTRS.get(full_key, '')
                is_diff = val_a != val_b
                if is_diff:
                    diffs += 1
                def _vkey(label):
                    for v in attr['values']:
                        if v['label'] == label:
                            return v['key']
                    return None
                dim_rows.append({
                    'attr': attr,
                    'dim_key': dim['key'],
                    'val_a': val_a,
                    'val_b': val_b,
                    'vkey_a': _vkey(val_a),
                    'vkey_b': _vkey(val_b),
                    'baseline': baseline,
                    'is_diff': is_diff,
                    'a_is_baseline': val_a == baseline,
                    'b_is_baseline': val_b == baseline,
                })
            rows.append({'dim': dim, 'attrs': dim_rows})
        comparison = {'rows': rows, 'diffs': diffs}

    return render(request, 'westminster_standards/compare_schools.html', {
        'schools': SCHOOLS,
        's_a': s_a,
        's_b': s_b,
        'comparison': comparison,
        'counts': _counts(),
    })


def cruxes_list(request):
    """All cruxes, grouped by locus, in the order of the eight loci."""
    groups = []
    for dim in DIMENSIONS:
        items = cruxes_by_locus(dim['key'])
        if items:
            groups.append({'dim': dim, 'cruxes': items})
    return render(request, 'westminster_standards/cruxes_list.html', {
        'groups': groups,
        'total': len(CRUXES),
        'counts': _counts(),
        'outcome_labels': _OUTCOME_LABELS,
    })


def crux_detail(request, slug):
    crux = get_crux_by_slug(slug)
    if not crux:
        raise Http404
    # Resolve the locus and the attributes the crux bears on.
    dim = _dimension_by_key(crux['locus_key'])
    attr_rows = _resolve_attr_rows(crux.get('attribute_keys', []))

    # Resolve persona slugs in parties to full persona objects.
    parties = []
    for party in crux.get('parties', []):
        people = []
        for slug_ in party.get('persona_slugs', []):
            p = get_persona_by_slug(slug_)
            if p:
                people.append(p)
        parties.append({
            'name': party.get('name', ''),
            'position': party.get('position', ''),
            'people': people,
        })

    # Linkify citations in the confessional-language quote and the
    # references list so that "WCF III.7" and "Larger Catechism Q. 50"
    # become hyperlinks to the loaded chapter/question text.
    language_html = linkify_citations(crux.get('language', ''))
    references_html = [linkify_citations(r) for r in crux.get('references', [])]

    # Resolve related cruxes for the "See also" section.
    related_cruxes = []
    for rslug in crux.get('related_crux_slugs', []):
        rc = get_crux_by_slug(rslug)
        if rc:
            related_cruxes.append(rc)

    # Schools mentioned in the legacy text.
    legacy_school_slugs = schools_mentioned_in_legacy(crux)
    legacy_schools = [get_school_by_slug(s) for s in legacy_school_slugs
                      if get_school_by_slug(s)]

    # Heads of doctrine that reference this crux.
    crux_heads = heads_for_crux(slug)

    return render(request, 'westminster_standards/crux_detail.html', {
        'crux': crux,
        'dim': dim,
        'attr_rows': attr_rows,
        'parties': parties,
        'outcome_label': _OUTCOME_LABELS.get(crux.get('outcome'), crux.get('outcome', '')),
        'language_html': language_html,
        'references_html': references_html,
        'related_cruxes': related_cruxes,
        'legacy_schools': legacy_schools,
        'crux_heads': crux_heads,
        'counts': _counts(),
    })


def schools_list(request):
    parties = [s for s in SCHOOLS if s['period'] == 'assembly-party']
    traditions = [s for s in SCHOOLS if s['period'] == 'receiving-tradition']
    return render(request, 'westminster_standards/schools_list.html', {
        'parties': parties,
        'traditions': traditions,
        'total': len(SCHOOLS),
        'counts': _counts(),
    })


def school_detail(request, slug):
    school = get_school_by_slug(slug)
    if not school:
        raise Http404
    # Resolve anchor personas.
    anchors = []
    for pslug in school.get('anchor_persona_slugs', []):
        p = get_persona_by_slug(pslug)
        if p:
            anchors.append(p)
    # Compute overrides vs baseline.
    override_rows = []
    for dim in DIMENSIONS:
        for attr in dim['attributes']:
            full_key = f"{dim['key']}_{attr['key']}"
            school_val = school['attrs'].get(full_key)
            baseline_val = WESTMINSTER_BASELINE_ATTRS.get(full_key)
            if school_val != baseline_val:
                value_key = None
                for v in attr['values']:
                    if v['label'] == school_val:
                        value_key = v['key']
                        break
                override_rows.append({
                    'dim': dim,
                    'attr': attr,
                    'value_label': school_val,
                    'value_key': value_key,
                    'baseline_label': baseline_val,
                })
    # Cruxes where this school's legacy is mentioned
    from .citations import schools_mentioned_in_legacy
    related_cruxes = []
    for cx in CRUXES:
        legacy_slugs = schools_mentioned_in_legacy(cx)
        if slug in legacy_slugs:
            related_cruxes.append(cx)
    # Also cruxes where anchor personas are parties
    anchor_set = set(school.get('anchor_persona_slugs', []))
    party_cruxes = []
    if anchor_set:
        for cx in CRUXES:
            for party in cx.get('parties', []):
                if anchor_set & set(party.get('persona_slugs', [])):
                    party_cruxes.append(cx)
                    break
    # Deduplicate
    seen = set()
    all_cruxes = []
    for cx in related_cruxes + party_cruxes:
        if cx['slug'] not in seen:
            seen.add(cx['slug'])
            all_cruxes.append(cx)

    return render(request, 'westminster_standards/school_detail.html', {
        'school': school,
        'anchors': anchors,
        'override_rows': override_rows,
        'related_cruxes': all_cruxes,
        'counts': _counts(),
    })


def works_list(request):
    return render(request, 'westminster_standards/works_list.html', {
        'works': WORKS,
        'counts': _counts(),
    })


def work_detail(request, slug):
    work = get_work_by_slug(slug)
    if not work:
        raise Http404
    # For catechisms, group questions by locus for collapsible display.
    question_groups = None
    if work.get('questions') and slug in ('wsc', 'wlc'):
        from collections import OrderedDict
        groups = OrderedDict()
        for q in work['questions']:
            loci = catechism_question_loci(slug, q['number'])
            locus_key = loci[0] if loci else 'other'
            dim = _dimension_by_key(locus_key)
            label = f"{dim['numeral']}. {dim['icon']} {dim['label']}" if dim else 'Other'
            if label not in groups:
                groups[label] = {'dim': dim, 'questions': []}
            groups[label]['questions'].append(q)
        question_groups = list(groups.values())
    # For directory-type works (DPW, FPCG, SSK), annotate each section
    # with its locus and related heads of doctrine.
    annotated_sections = None
    if work.get('is_directory') and work.get('chapters') and slug in ('dpw', 'fpcg', 'ssk'):
        from .heads_of_doctrine import HEADS_OF_DOCTRINE
        annotated_sections = []
        for sec in work['chapters']:
            loci_keys = directory_section_loci(slug, sec['number'])
            loci = [d for d in DIMENSIONS if d['key'] in loci_keys]
            # Find heads that relate to this section's locus
            related_heads = []
            for h in HEADS_OF_DOCTRINE:
                if h.get('locus_key') in loci_keys:
                    related_heads.append(h)
            # Deduplicate and limit to most relevant
            seen = set()
            unique_heads = []
            for h in related_heads:
                if h['slug'] not in seen:
                    seen.add(h['slug'])
                    unique_heads.append(h)
            # Ontology tags for the section: the union of the ontology
            # attributes carried by the heads shown for this section.
            attr_rows = _resolve_attr_rows(
                attribute_tags_for_heads(unique_heads[:5]))
            annotated_sections.append({
                'section': sec,
                'loci': loci,
                'heads': unique_heads[:5],
                'attrs': attr_rows,
            })
    has_rep_tags = bool(annotated_sections) and any(
        r['representative'] for s in annotated_sections for r in s['attrs'])
    return render(request, 'westminster_standards/work_detail.html', {
        'work': work,
        'question_groups': question_groups,
        'annotated_sections': annotated_sections,
        'has_rep_tags': has_rep_tags,
        'counts': _counts(),
    })


def wcf_chapter_detail(request, number):
    try:
        n = int(number)
    except (TypeError, ValueError):
        raise Http404
    chapter = get_wcf_chapter(n)
    if not chapter:
        raise Http404
    wcf = get_work_by_slug('wcf')
    chapters = wcf.get('chapters') or []
    prev_ch = next((c for c in chapters if c['number'] == n - 1), None)
    next_ch = next((c for c in chapters if c['number'] == n + 1), None)
    related_cruxes = cruxes_for_wcf_chapter(n)
    locus_keys = wcf_chapter_loci(n)
    loci = [d for d in DIMENSIONS if d['key'] in locus_keys]
    # Build a map of section number -> heads and -> ontology attribute rows
    # for cross-linking. The ontology tags are derived from the heads that
    # cover each section (see heads_of_doctrine.attributes_for_wcf_section).
    section_heads = {}
    section_attrs = {}
    for s in chapter.get('sections', []):
        sh = heads_for_wcf_section(n, s['number'])
        if sh:
            section_heads[s['number']] = sh
        attr_rows = _resolve_attr_rows(attribute_tags_for_wcf_section(n, s['number']))
        if attr_rows:
            section_attrs[s['number']] = attr_rows
    has_rep_tags = any(r['representative']
                       for rows in section_attrs.values() for r in rows)
    return render(request, 'westminster_standards/wcf_chapter.html', {
        'work': wcf,
        'chapter': chapter,
        'prev_chapter': prev_ch,
        'next_chapter': next_ch,
        'related_cruxes': related_cruxes,
        'section_heads': section_heads,
        'section_attrs': section_attrs,
        'has_rep_tags': has_rep_tags,
        'loci': loci,
        'counts': _counts(),
    })


def _catechism_cross_refs(catechism_slug, n, limit=12):
    """Parallel treatment of a catechism question elsewhere in the Standards.

    Using the Heads of Doctrine index (which maps each systematic topic to the
    WCF sections, Shorter-Catechism, and Larger-Catechism questions that treat
    it), gather the Confession sections and the *other* catechism's questions
    that fall under the same head(s) as this question. This lets a bare Q&A
    page show how the same doctrine is handled across all three documents.
    """
    from .heads_of_doctrine import HEADS_OF_DOCTRINE
    other = 'wlc' if catechism_slug == 'wsc' else 'wsc'
    wcf_pairs, other_qs = [], []
    seen_wcf, seen_q = set(), set()
    for h in HEADS_OF_DOCTRINE:
        own_list = h['wsc_questions'] if catechism_slug == 'wsc' else h['wlc_questions']
        if n not in own_list:
            continue
        for cs in h['wcf_sections']:
            t = tuple(cs)
            if t not in seen_wcf:
                seen_wcf.add(t)
                wcf_pairs.append(t)
        other_list = h['wlc_questions'] if other == 'wlc' else h['wsc_questions']
        for qn in other_list:
            if qn not in seen_q:
                seen_q.add(qn)
                other_qs.append(qn)

    wcf_total, other_total = len(wcf_pairs), len(other_qs)
    wcf_sections = []
    for ch_num, sec_num in wcf_pairs[:limit]:
        chapter = get_wcf_chapter(ch_num)
        if chapter:
            for s in chapter.get('sections', []):
                if s['number'] == sec_num:
                    wcf_sections.append({'chapter': chapter, 'section': s})
                    break
    other_questions = []
    for qn in other_qs[:limit]:
        qq = get_catechism_question(other, qn)
        if qq:
            other_questions.append(qq)
    other_work = get_work_by_slug(other)
    return {
        'other_slug': other,
        'other_title': other_work['title'] if other_work else other.upper(),
        'wcf_sections': wcf_sections,
        'wcf_more': max(0, wcf_total - len(wcf_sections)),
        'other_questions': other_questions,
        'other_more': max(0, other_total - len(other_questions)),
    }


def catechism_question_detail(request, catechism_slug, number):
    cat = get_work_by_slug(catechism_slug)
    if not cat or cat.get('form') != 'Catechism':
        raise Http404
    try:
        n = int(number)
    except (TypeError, ValueError):
        raise Http404
    q = get_catechism_question(catechism_slug, n)
    if not q:
        raise Http404
    questions = cat.get('questions') or []
    prev_q = next((x for x in questions if x['number'] == n - 1), None)
    next_q = next((x for x in questions if x['number'] == n + 1), None)
    related_cruxes = cruxes_for_catechism_question(catechism_slug, n)
    locus_keys = catechism_question_loci(catechism_slug, n)
    loci = [d for d in DIMENSIONS if d['key'] in locus_keys]
    question_heads = heads_for_catechism_question(catechism_slug, n)
    question_attrs = _resolve_attr_rows(
        attribute_tags_for_catechism_question(catechism_slug, n))
    cross_refs = _catechism_cross_refs(catechism_slug, n)
    answer_html = _answer_with_markers(q.get('answer_with_proofs') or q['answer'],
                                       len(q.get('proofs') or []))
    return render(request, 'westminster_standards/catechism_question.html', {
        'work': cat,
        'question': q,
        'answer_html': answer_html,
        'prev_question': prev_q,
        'next_question': next_q,
        'related_cruxes': related_cruxes,
        'question_heads': question_heads,
        'question_attrs': question_attrs,
        'has_rep_tags': any(r['representative'] for r in question_attrs),
        'cross_refs': cross_refs,
        'loci': loci,
        'counts': _counts(),
    })


_MARKER_RE = re.compile(r'\[(\d+)\]')


def _answer_with_markers(answer_with_proofs, proof_count):
    """Render a catechism answer as safe HTML, turning each ``[n]`` proof
    marker into a superscript link to the matching proof clause below."""
    text = escape(answer_with_proofs)

    def repl(m):
        nid = m.group(1)
        if not (1 <= int(nid) <= proof_count):
            return ''                       # stray marker with no matching proof
        return (f'<sup class="ws-pm"><a href="#proof-{nid}" '
                f'title="Scripture proof {nid}">{nid}</a></sup>')

    return mark_safe(_MARKER_RE.sub(repl, text))


def _dim_of(full_key, dims):
    """The dimension of a ``dimkey_attrkey`` full key.

    Split against the known dimensions rather than on the last underscore:
    both halves contain underscores (``god_decree_extent_of_atonement``).
    """
    for dimension in dims:
        if full_key.startswith(dimension['key'] + '_'):
            return dimension['key']
    return ''


def _attr_of(full_key, dims):
    dim_key = _dim_of(full_key, dims)
    return full_key[len(dim_key) + 1:] if dim_key else full_key


def _intersection_clusters(dim_keys):
    """For the given set of dimensions, build a cluster view grouping
    personas and schools by their joint signature across the selected loci."""
    dims = [d for d in DIMENSIONS if d['key'] in dim_keys]
    attr_keys = []
    attr_labels_local = {}
    for d in dims:
        for a in d['attributes']:
            full = f"{d['key']}_{a['key']}"
            attr_keys.append(full)
            attr_labels_local[full] = a['label']

    def signature(entity):
        return tuple(entity.get('attrs', {}).get(k, '—') for k in attr_keys)

    clusters = {}
    for school in SCHOOLS:
        sig = signature(school)
        clusters.setdefault(sig, {'schools': [], 'personas': []})['schools'].append(school)
    for persona in PERSONAS:
        sig = signature(persona)
        clusters.setdefault(sig, {'schools': [], 'personas': []})['personas'].append(persona)

    view = []
    for sig, members in clusters.items():
        if not members['schools'] and not members['personas']:
            continue
        view.append({
            'values': [
                {
                    'attr_label': attr_labels_local[key],
                    'dim_key': _dim_of(key, dims),
                    'attr_key': _attr_of(key, dims),
                    'value_label': value,
                }
                for key, value in zip(attr_keys, sig)
            ],
            'schools': members['schools'],
            'personas': members['personas'],
            'count': len(members['schools']) + len(members['personas']),
        })
    view.sort(key=lambda c: -c['count'])
    return view, dims


def dimension_pairs(request):
    items = []
    for combo in DIMENSION_PAIRS:
        items.append({
            'key': '-'.join(combo),
            'labels': [(_dimension_by_key(k) or {}).get('label', k) for k in combo],
            'icons': [(_dimension_by_key(k) or {}).get('icon', '') for k in combo],
        })
    return render(request, 'westminster_standards/dimension_pairs.html', {
        'items': items, 'n': 2, 'counts': _counts(),
    })


def dimension_pair_detail(request, pair_key):
    keys = pair_key.split('-')
    dims = [_dimension_by_key(k) for k in keys]
    if any(d is None for d in dims):
        raise Http404
    clusters, _ = _intersection_clusters(keys)
    return render(request, 'westminster_standards/dimension_pair_detail.html', {
        'dims': dims, 'pair_key': pair_key, 'clusters': clusters,
        'counts': _counts(),
    })


def search(request):
    q = (request.GET.get('q') or '').strip()
    results = {'personas': [], 'cruxes': [], 'schools': [], 'heads': [], 'wcf_chapters': [], 'catechism_qs': []}
    if q and len(q) >= 2:
        ql = q.lower()

        for h in HEADS_OF_DOCTRINE:
            if (ql in h['name'].lower() or ql in h.get('description', '').lower()):
                results['heads'].append(h)

        for p in PERSONAS:
            if (ql in p['name'].lower() or ql in p.get('bio', '').lower()
                    or ql in p.get('tagline', '').lower()
                    or ql in p.get('role', '').lower()):
                results['personas'].append(p)

        for c in CRUXES:
            if (ql in c['title'].lower() or ql in c.get('tagline', '').lower()
                    or ql in c.get('summary', '').lower()
                    or ql in c.get('background', '').lower()
                    or ql in c.get('language', '').lower()):
                results['cruxes'].append(c)

        for s in SCHOOLS:
            if (ql in s['name'].lower() or ql in s.get('description', '').lower()
                    or ql in s.get('origin', '').lower()):
                results['schools'].append(s)

        wcf = get_work_by_slug('wcf')
        if wcf:
            for ch in wcf.get('chapters') or []:
                if ql in ch['title'].lower():
                    results['wcf_chapters'].append(ch)
                    continue
                for sec in ch.get('sections') or []:
                    if ql in sec['content'].lower():
                        results['wcf_chapters'].append(ch)
                        break

        # Search DPW, FPCG, SSK sections
        for dir_slug in ('dpw', 'fpcg', 'ssk'):
            work = get_work_by_slug(dir_slug)
            if work and work.get('chapters'):
                for sec in work['chapters']:
                    if (ql in sec['title'].lower()
                            or ql in sec.get('content', '').lower()):
                        results.setdefault('directory_sections', []).append({
                            'work_slug': dir_slug,
                            'work_title': work['short_title'],
                            'section': sec,
                        })

        for cat_slug in ('wsc', 'wlc'):
            cat = get_work_by_slug(cat_slug)
            if cat:
                for qn in cat.get('questions') or []:
                    if (ql in qn['question'].lower()
                            or ql in qn['answer'].lower()):
                        results['catechism_qs'].append({
                            'cat_slug': cat_slug,
                            'cat_title': cat['short_title'],
                            'q': qn,
                        })

    total = sum(len(v) for v in results.values())
    return render(request, 'westminster_standards/search.html', {
        'q': q,
        'results': results,
        'total': total,
        'counts': _counts(),
    })


def value_detail(request, dim_key, attr_key, value_key):
    dim = _dimension_by_key(dim_key)
    if not dim:
        raise Http404
    attr = next((a for a in dim['attributes'] if a['key'] == attr_key), None)
    if not attr:
        raise Http404
    value = next((v for v in attr['values'] if v['key'] == value_key), None)
    if not value:
        raise Http404
    full_key = f"{dim_key}_{attr_key}"
    baseline_label = WESTMINSTER_BASELINE_ATTRS.get(full_key)
    is_baseline = (baseline_label == value['label'])
    siblings = [v for v in attr['values'] if v['key'] != value_key]

    # Personas and schools that hold this value
    target_label = value['label']
    personas_here = [p for p in PERSONAS if p['attrs'].get(full_key) == target_label]
    schools_here = [s for s in SCHOOLS if s['attrs'].get(full_key) == target_label]

    # Cruxes that bear on this attribute
    attr_cruxes = [cx for cx in CRUXES if full_key in cx.get('attribute_keys', [])]

    return render(request, 'westminster_standards/value_detail.html', {
        'dim': dim,
        'attr': attr,
        'value': value,
        'siblings': siblings,
        'is_baseline': is_baseline,
        'baseline_label': baseline_label,
        'personas_here': personas_here,
        'schools_here': schools_here,
        'attr_cruxes': attr_cruxes,
        'counts': _counts(),
    })


def heads_list(request):
    """All heads of doctrine, grouped by locus, in the order of the eight loci."""
    groups = []
    for dim in DIMENSIONS:
        items = heads_by_locus(dim['key'])
        if items:
            annotated = []
            for h in items:
                annotated.append({
                    'head': h,
                    'wcf_count': len(h['wcf_sections']),
                    'wsc_count': len(h['wsc_questions']),
                    'wlc_count': len(h['wlc_questions']),
                    'crux_count': len(h['related_crux_slugs']),
                })
            groups.append({'dim': dim, 'heads': annotated})
    return render(request, 'westminster_standards/heads_list.html', {
        'groups': groups,
        'total': len(HEADS_OF_DOCTRINE),
        'counts': _counts(),
    })


def head_detail(request, slug):
    head = get_head_by_slug(slug)
    if not head:
        raise Http404

    dim = _dimension_by_key(head['locus_key'])

    # Fetch the actual WCF section texts.
    wcf_section_texts = []
    for ch_num, sec_num in head['wcf_sections']:
        chapter = get_wcf_chapter(ch_num)
        if chapter:
            for s in chapter.get('sections', []):
                if s['number'] == sec_num:
                    wcf_section_texts.append({
                        'chapter': chapter,
                        'section': s,
                    })
                    break

    # Fetch the catechism Q&A texts.
    wsc_questions = []
    for qn in head['wsc_questions']:
        q = get_catechism_question('wsc', qn)
        if q:
            wsc_questions.append(q)

    wlc_questions = []
    for qn in head['wlc_questions']:
        q = get_catechism_question('wlc', qn)
        if q:
            wlc_questions.append(q)

    # Resolve related cruxes.
    related_cruxes = []
    for cs in head.get('related_crux_slugs', []):
        crux = get_crux_by_slug(cs)
        if crux:
            related_cruxes.append(crux)

    # Find personas whose attrs differ from baseline on this head's locus.
    related_personas = []
    locus_key = head['locus_key']
    locus_attrs = []
    if dim:
        for attr in dim['attributes']:
            locus_attrs.append(f"{dim['key']}_{attr['key']}")
    for p in PERSONAS:
        for fk in locus_attrs:
            if p['attrs'].get(fk) != WESTMINSTER_BASELINE_ATTRS.get(fk):
                related_personas.append(p)
                break
    # Limit to first 20 for display.
    related_personas = related_personas[:20]

    # Fetch DPW/FPCG/SSK section texts — separate lists for each work.
    dpw_section_texts = []
    fpcg_section_texts = []
    ssk_section_texts = []
    for dir_slug, dir_label, target_list in [
        ('dpw', 'Directory for Public Worship', dpw_section_texts),
        ('fpcg', 'Form of Church Government', fpcg_section_texts),
        ('ssk', 'Sum of Saving Knowledge', ssk_section_texts),
    ]:
        sec_nums = head.get(f'{dir_slug}_sections', [])
        if sec_nums:
            work = get_work_by_slug(dir_slug)
            if work and work.get('chapters'):
                for sec in work['chapters']:
                    if sec['number'] in sec_nums:
                        target_list.append(sec)

    return render(request, 'westminster_standards/head_detail.html', {
        'head': head,
        'dim': dim,
        'wcf_section_texts': wcf_section_texts,
        'wsc_questions': wsc_questions,
        'wlc_questions': wlc_questions,
        'dpw_section_texts': dpw_section_texts,
        'fpcg_section_texts': fpcg_section_texts,
        'ssk_section_texts': ssk_section_texts,
        'related_cruxes': related_cruxes,
        'related_personas': related_personas,
        'counts': _counts(),
    })
