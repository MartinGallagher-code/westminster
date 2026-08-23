"""Build a printable session handout for a question or a whole chapter.

Small groups need something to put in front of people: the text, the proofs
behind it, a few questions worth arguing about, and enough background for
whoever is leading. All of that already exists in the database — proof texts,
cross-references between the standards, the Atlas's record of what the
Assembly actually debated, and the commentators — so the handout assembles it
rather than inventing it.

The discussion prompts are deliberately built from *this passage's* own
material. A generic prompt ("what does this teach us?") is worse than none.
"""

from .models import ScripturePassage, StandardCrossReference

MAX_PROMPTS = 4
MAX_LEADER_NOTES = 3
LEADER_NOTE_WORDS = 120


def _truncate_words(text, limit):
    words = (text or '').split()
    if len(words) <= limit:
        return ' '.join(words)
    return ' '.join(words[:limit]).rstrip('.,;:') + '…'


def _proof_passages(question):
    """Proof references for a question, with their text where it is loaded."""
    references = question.get_proof_text_list()
    if not references:
        return []
    loaded = {
        passage.reference: passage.text
        for passage in ScripturePassage.objects.filter(reference__in=references)
    }
    return [
        {'reference': reference, 'text': loaded.get(reference, '')}
        for reference in references
    ]


def _cross_references(question):
    """Where the other standards treat the same ground."""
    links = StandardCrossReference.objects.filter(
        source_question=question,
    ).select_related('target_question__catechism', 'target_question__topic')
    return [link.target_question for link in links]


def _cruxes_for(question):
    """Assembly debates that bear on this passage, from the Atlas."""
    slug = question.catechism.slug
    if slug not in ('wcf', 'wsc', 'wlc'):
        return []

    from westminster_standards.cruxes import CRUXES
    from westminster_standards.heads_of_doctrine import (
        heads_for_catechism_question, heads_for_wcf_section,
    )

    if slug == 'wcf':
        if not question.topic:
            return []
        section = question.number - question.topic.question_start + 1
        heads = heads_for_wcf_section(question.topic.order, section)
    else:
        heads = heads_for_catechism_question(slug, question.number)

    wanted = {
        crux_slug for head in heads for crux_slug in head.get('related_crux_slugs', [])
    }
    return [crux for crux in CRUXES if crux['slug'] in wanted]


def discussion_prompts(question, proofs, cross_references, cruxes):
    """Questions worth arguing about, grounded in this passage's own material."""
    prompts = []

    if proofs:
        first = proofs[0]['reference']
        prompts.append(
            f'The Assembly cited {first} in support of this answer. '
            'Read it in context — how does it bear on what is claimed here?'
        )
    if len(proofs) > 1:
        prompts.append(
            f'{len(proofs)} passages are cited here. Which does the most work, '
            'and is anything claimed that the proofs do not obviously carry?'
        )
    for target in cross_references[:2]:
        prompts.append(
            f'{target.catechism.abbreviation} '
            f'{target.catechism.item_prefix}{target.display_number} treats the same '
            'ground. What does it add, and why might it put things differently?'
        )
    for crux in cruxes[:2]:
        prompts.append(
            f'The Assembly divided over this: {crux["title"]}. '
            f'{crux.get("tagline", "")} What turns on the answer?'.strip()
        )

    if not prompts:
        prompts.append(
            'Put this answer in your own words, then say what it rules out — '
            'what belief is it written against?'
        )
    return prompts[:MAX_PROMPTS]


def leader_notes(question):
    """Short extracts from the loaded commentators, with attribution."""
    notes = []
    commentaries = question.commentaries.select_related('source').all()
    for commentary in commentaries[:MAX_LEADER_NOTES]:
        body = _truncate_words(commentary.body, LEADER_NOTE_WORDS)
        if body:
            notes.append({
                'source': commentary.source.name,
                'author': getattr(commentary.source, 'author', ''),
                'body': body,
            })
    return notes


def build_item(question):
    """Everything the handout shows for one question or section."""
    proofs = _proof_passages(question)
    cross_references = _cross_references(question)
    cruxes = _cruxes_for(question)
    return {
        'question': question,
        'proofs': proofs,
        'cross_references': cross_references,
        'cruxes': cruxes,
        'prompts': discussion_prompts(question, proofs, cross_references, cruxes),
        'leader_notes': leader_notes(question),
    }


def build_handout(questions):
    """A handout covering one or more questions, in order."""
    return [build_item(question) for question in questions]
