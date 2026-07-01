"""Westminster Works — the Standards themselves and the supporting documents.

The corpus:

  1. The Westminster Confession of Faith (1646/47)              — 33 chapters
  2. The Westminster Larger Catechism (1647)                    — 196 Q&As
  3. The Westminster Shorter Catechism (1647)                   — 107 Q&As
  4. The Directory for the Public Worship of God (1645)         — service-book
  5. The Form of Presbyterial Church Government (1645)          — polity
  6. The Sum of Saving Knowledge (1650 Scottish addendum)       — appendix

The full text of #1, #2, and #3 is loaded at import time from the
JSON files in ``westminster_standards/raw/``, sourced from the
NonlinearFruit/Creeds.json GitHub repository (MIT licence on the
structure; the texts themselves are 17th-century public domain).
Source URLs and attribution are recorded in ``WORKS_METADATA``.

Layer-data conventions:

  - ``slug`` — URL-safe identifier (e.g. 'wcf', 'wlc', 'wsc')
  - ``title`` / ``short_title`` / ``year``
  - ``form`` — 'Confession', 'Catechism', 'Directory', 'Form'
  - ``summary`` — one-paragraph description
  - ``chapters`` (WCF) or ``questions`` (catechisms) — the parsed content
  - ``source_attribution`` / ``source_url`` — provenance

Each WCF chapter has ``number``, ``title``, ``slug``, and ``sections``
(each with ``number``, ``content``, ``content_with_proofs``, ``proofs``).

Each catechism question has ``number``, ``question``, ``answer``, and
(LC only) ``answer_with_proofs`` and ``proofs``.
"""

import json
import os
import re

from .data import WESTMINSTER_BASELINE_ATTRS
from .scripture import pretty_ref


_RAW_DIR = os.path.join(os.path.dirname(__file__), 'raw')


def _slugify(text):
    """Lowercase, hyphenated, alphanumeric-only slug from a chapter title."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def _load_json(filename):
    path = os.path.join(_RAW_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_proof_verses():
    """Map raw proof-reference string -> list of {'ref', 't'} KJV verses.

    Built offline by scripts/build_proof_verses.py. Missing file degrades
    gracefully (references simply show no verse text)."""
    try:
        return _load_json('proof_verses.json')
    except FileNotFoundError:
        return {}


_PROOF_VERSES = _load_proof_verses()


# ----------------------------------------------------------------------
# Load the WCF
# ----------------------------------------------------------------------

def _load_wcf():
    raw = _load_json('westminster_confession_of_faith.json')
    md = raw['Metadata']
    chapters = []
    for ch in raw['Data']:
        title = ch.get('Title', '').strip() or f"Chapter {ch['Chapter']}"
        chapters.append({
            'number': int(ch['Chapter']),
            'roman': _arabic_to_roman(int(ch['Chapter'])),
            'title': title,
            'slug': _slugify(title),
            'sections': [
                {
                    'number': int(s.get('Section', i + 1)),
                    'content': s['Content'],
                    'content_with_proofs': s.get('ContentWithProofs', s['Content']),
                    'proofs': s.get('Proofs', []),
                }
                for i, s in enumerate(ch['Sections'])
            ],
        })
    return {
        'slug': 'wcf',
        'title': md.get('Title', 'Westminster Confession of Faith'),
        'short_title': 'WCF',
        'year': md.get('Year', '1647'),
        'form': 'Confession',
        'summary': (
            "The thirty-three chapters of the Confession, the principal "
            "doctrinal output of the Westminster Assembly, completed in 1646 "
            "and presented to the Long Parliament in December of that year. "
            "Each chapter is divided into sections; this edition includes the "
            "proof-text apparatus."
        ),
        'author': 'The Westminster Assembly',
        'date_completed': '1646 (text); 1647 (parliamentary approval)',
        'source_attribution': md.get('SourceAttribution', 'Public Domain'),
        'source_url': md.get('SourceUrl', ''),
        'chapters': chapters,
        'questions': None,
    }


def _arabic_to_roman(n):
    pairs = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
    ]
    out = []
    for value, sym in pairs:
        while n >= value:
            out.append(sym)
            n -= value
    return ''.join(out)


# ----------------------------------------------------------------------
# Load the Catechisms
# ----------------------------------------------------------------------

def _load_catechism(filename, slug, short_title, summary):
    raw = _load_json(filename)
    md = raw['Metadata']
    questions = []
    for q in raw['Data']:
        proofs = []
        for proof in q.get('Proofs', []):
            references = []
            for r in proof.get('References', []):
                references.append({
                    'ref': pretty_ref(r),
                    'verses': _PROOF_VERSES.get(r, []),
                })
            proofs.append({
                'Id': proof.get('Id'),
                'References': references,
            })
        questions.append({
            'number': int(q['Number']),
            'question': q['Question'],
            'answer': q['Answer'],
            'answer_with_proofs': q.get('AnswerWithProofs', q['Answer']),
            'proofs': proofs,
        })
    return {
        'slug': slug,
        'title': md.get('Title'),
        'short_title': short_title,
        'year': md.get('Year', '1647'),
        'form': 'Catechism',
        'summary': summary,
        'author': 'The Westminster Assembly',
        'date_completed': '1647',
        'source_attribution': md.get('SourceAttribution', 'Public Domain'),
        'source_url': md.get('SourceUrl', ''),
        'chapters': None,
        'questions': questions,
    }


def _load_dpw():
    """Load the Directory for Public Worship from the plain-text file."""
    return _load_directory_text(
        'directory_for_public_worship.txt',
        'dpw', 'DPW',
        'The Directory for the Public Worship of God',
        '1645',
        "The service-book that replaced the Book of Common Prayer in "
        "Reformed worship under the Long Parliament. Where the BCP had "
        "prescribed fixed forms of prayer, the Directory prescribes "
        "the ordering and substance of worship but leaves the wording "
        "to the minister's free pastoral prayer. This is the practical "
        "application of the regulative principle (WCF XXI). Adopted by "
        "the Long Parliament on 3 January 1645 and by the Scottish "
        "General Assembly on 3 February 1645.",
    )


def _load_fpcg():
    """Load the Form of Presbyterial Church Government from plain text."""
    return _load_directory_text(
        'form_of_presbyterial_church_government.txt',
        'fpcg', 'FPCG',
        'The Form of Presbyterial Church Government',
        '1645',
        "The polity document of the Assembly, prescribing the graded "
        "courts of presbyterian government (session, presbytery, synod, "
        "general assembly) and the four offices (pastor, teacher, ruling "
        "elder, deacon). This is the procedural companion to WCF "
        "XXV-XXXI: where the Confession states the principles of "
        "church government confessionally, the Form provides the "
        "operational detail. The Scottish General Assembly approved it "
        "on 10 February 1645.",
    )


def _load_directory_text(filename, slug, short_title, title, year, summary):
    """Generic loader for plain-text ---SECTION--- delimited documents."""
    path = os.path.join(_RAW_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    raw_sections = text.split('---SECTION---')
    sections = []
    for i, raw in enumerate(raw_sections[1:], 1):
        lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
        if not lines:
            continue
        sec_title = lines[0].rstrip('.')
        body = '\n\n'.join(lines[1:])
        sections.append({
            'number': i,
            'title': sec_title,
            'slug': _slugify(sec_title),
            'content': body,
        })
    return {
        'slug': slug,
        'title': title,
        'short_title': short_title,
        'year': year,
        'form': 'Directory' if slug == 'dpw' else 'Form',
        'summary': summary,
        'author': 'The Westminster Assembly',
        'date_completed': year,
        'source_attribution': 'Public Domain (' + year + ')',
        'source_url': '',
        'chapters': sections,
        'questions': None,
        'is_directory': True,
    }


def _load_ssk():
    """Load the Sum of Saving Knowledge from plain text."""
    return _load_directory_text(
        'sum_of_saving_knowledge.txt',
        'ssk', 'SSK',
        'The Sum of Saving Knowledge',
        '1650',
        "Composed by David Dickson (Professor of Divinity at Glasgow) "
        "and James Durham (minister at Glasgow) around 1650. Not "
        "strictly a Westminster document, but bound with the Standards "
        "in Scottish editions from the mid-17th century. Four heads "
        "on man's condition by nature, the remedy in Christ, the means "
        "of the covenant of grace, and the blessings conveyed; followed "
        "by practical application on convincing of sin, warrants to "
        "believe, and evidences of true faith.",
    )


# ----------------------------------------------------------------------
# Standards that are not yet loaded as full text
# ----------------------------------------------------------------------

_STUB_WORKS = []


# ----------------------------------------------------------------------
# Build the WORKS list
# ----------------------------------------------------------------------

WORKS = []

try:
    WORKS.append(_load_wcf())
except FileNotFoundError:
    pass

try:
    WORKS.append(_load_catechism(
        'westminster_larger_catechism.json',
        'wlc', 'WLC',
        "196 questions and answers, the larger of the Assembly's two "
        "catechisms, intended chiefly for instruction in the family and the "
        "ministerial training of candidates. Its expositions of the "
        "Decalogue (Q. 91-148), the Lord's Prayer (Q. 178-196), and the "
        "Apostles' Creed material are exceptionally detailed.",
    ))
except FileNotFoundError:
    pass

try:
    WORKS.append(_load_catechism(
        'westminster_shorter_catechism.json',
        'wsc', 'WSC',
        "107 questions and answers, the shorter of the Assembly's two "
        "catechisms, intended chiefly for instruction of children and the "
        "young in the faith. Its opening question — 'What is the chief end "
        "of man? Man's chief end is to glorify God, and to enjoy him "
        "forever.' — is one of the most influential single sentences in "
        "English Reformed theology.",
    ))
except FileNotFoundError:
    pass

try:
    WORKS.append(_load_dpw())
except FileNotFoundError:
    pass

try:
    WORKS.append(_load_fpcg())
except FileNotFoundError:
    pass

try:
    WORKS.append(_load_ssk())
except FileNotFoundError:
    pass

WORKS.extend(_STUB_WORKS)


# ----------------------------------------------------------------------
# Lookup helpers
# ----------------------------------------------------------------------


def get_work_by_slug(slug):
    for w in WORKS:
        if w.get('slug') == slug:
            return w
    return None


def get_wcf_chapter(number):
    wcf = get_work_by_slug('wcf')
    if not wcf:
        return None
    for ch in wcf.get('chapters') or []:
        if ch['number'] == number:
            return ch
    return None


def get_catechism_question(catechism_slug, number):
    cat = get_work_by_slug(catechism_slug)
    if not cat:
        return None
    for q in cat.get('questions') or []:
        if q['number'] == number:
            return q
    return None
