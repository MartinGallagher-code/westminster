"""The PCA Book of Church Order: its data, its numbering, and its reloads."""

import importlib.util
import json
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

from catechism.citations import citation_label, reference_slug, resolve_reference
from catechism.management.commands import load_pca_bco
from catechism.management.commands.check_bco_update import current_pdf_url
from catechism.models import Catechism, Question, StandardCrossReference, Topic
from catechism.templatetags.catechism_tags import format_paragraphs

DATA_PATH = Path(settings.BASE_DIR) / 'data' / 'pca_bco' / 'pca_bco.json'


def _sections(data):
    for part in data['parts']:
        for chapter in part['chapters']:
            for section in chapter['sections']:
                yield chapter, section


@pytest.fixture(scope='module')
def bco_data():
    with open(DATA_PATH) as f:
        return json.load(f)


# ── The committed data ──────────────────────────────────────────────────


def test_every_chapter_is_present_in_order(bco_data):
    chapters = [c['chapter'] for p in bco_data['parts'] for c in p['chapters']]
    assert chapters == list(range(1, 64))
    vacated = [c for p in bco_data['parts'] for c in p['chapters'] if not c['sections']]
    assert [c['chapter'] for c in vacated] == [44]


def test_sections_are_numbered_consecutively_within_each_chapter(bco_data):
    for chapter, section in _sections(bco_data):
        number, position = section['number'].split('-')
        assert int(number) == chapter['chapter']
    for part in bco_data['parts']:
        for chapter in part['chapters']:
            numbers = [int(s['number'].split('-')[1]) for s in chapter['sections']]
            assert numbers == list(range(1, len(numbers) + 1)), chapter['chapter']


def test_no_typesetting_leaks_into_the_text(bco_data):
    """Running headers, bookmark labels and amendment bullets are page furniture."""
    texts = [p['text'] for p in bco_data['preface']]
    texts += [s['text'] for _, s in _sections(bco_data)]
    for text in texts:
        assert 'THE BOOK OF CHURCH ORDER' not in text
        assert not re.search('[-]', text)
        # A section's own number is the reference, not part of its text.
        assert not re.match(r'\d+-\d+\.', text)


def test_no_section_swallowed_the_next(bco_data):
    """56-6 is printed without its period and was once merged into 56-5."""
    for _, section in _sections(bco_data):
        for paragraph in section['text'].split('\n\n'):
            assert not re.match(r'\d{1,2}-\d{1,2}\.? [A-Z]', paragraph), section['number']
    numbers = {s['number'] for _, s in _sections(bco_data)}
    assert {'56-6', '36-8'} <= numbers


def test_no_chapter_title_trails_the_previous_chapter(bco_data):
    """Chapter headings were once appended to the last section before them."""
    titles = [c['title'] for p in bco_data['parts'] for c in p['chapters'] if c['title'] != '(Vacated)']
    for _, section in _sections(bco_data):
        last = section['text'].split('\n\n')[-1].strip()
        assert last not in titles, section['number']


def test_lists_are_separate_paragraphs(bco_data):
    sections = {s['number']: s for _, s in _sections(bco_data)}
    paragraphs = sections['12-5']['text'].split('\n\n')
    assert [p[:2] for p in paragraphs[1:]] == ['a.', 'b.', 'c.', 'd.', 'e.', 'f.']


def test_footnotes_stay_with_their_sections(bco_data):
    sections = {s['number']: s for _, s in _sections(bco_data)}
    assert sections['21-5']['text'].endswith(
        'Note: For an assistant minister, only questions 1-7 shall be used.'
    )
    assert 'Note: For assistant minister' not in sections['21-8']['text']
    assert sections['13-9']['text'].endswith('Editor\'s note: "Issue" means "settling the issue of the case."')


def test_2026_amendments_are_present(bco_data):
    """Amendments ratified at the 53rd General Assembly (2026)."""
    sections = {s['number']: s for _, s in _sections(bco_data)}
    assert bco_data['year'] == 2026
    assert '53rd General Assembly' in bco_data['edition']
    assert 'incorrigible and contumacious' in sections['36-8']['text']
    assert 'Scripture as interpreted in these Standards' in sections['29-1']['text']
    assert 'those appealing the elevation of a censure under BCO 36-8' in sections['42-2']['text']


def test_directory_for_worship_preface_is_kept_apart(bco_data):
    part_three = bco_data['parts'][2]
    assert part_three['introduction'].startswith('Temporary statement adopted by the Third General Assembly')
    sections = {s['number']: s for _, s in _sections(bco_data)}
    assert 'Temporary statement' not in sections['46-8']['text']


def test_scripture_citations_are_keyed_by_reference():
    with open(Path(settings.BASE_DIR) / 'data' / 'pca-bco_proof_texts.json') as f:
        citations = json.load(f)
    assert citations['Preface I'] == 'Isaiah 9:6-7; Ephesians 1:20-23; Ephesians 4:10-13'
    assert citations['59-3'] == 'Gen. 2:24, 25; Matt. 19:4-6; 1 Cor. 7:2'
    assert all(re.match(r'^(Preface [IV]+|\d+-\d+)$', key) for key in citations)


def test_parser_scripture_extraction():
    path = Path(settings.BASE_DIR) / 'scripts' / 'parse_pca_bco.py'
    spec = importlib.util.spec_from_file_location('parse_pca_bco', path)
    module = importlib.util.module_from_spec(spec)
    pytest.importorskip('pdfplumber')
    spec.loader.exec_module(module)
    text = 'Christ (Matt. 19:4-6, 1 Cor. 7:2) and (Gen. 2:24, 25); again Matt. 19:4-6.'
    assert module.scripture_references(text) == ['Matt. 19:4-6', '1 Cor. 7:2', 'Gen. 2:24, 25']


# ── Loading ─────────────────────────────────────────────────────────────


@pytest.fixture
def bco(db):
    call_command('load_pca_bco')
    return Catechism.objects.get(slug='pca-bco')


def _section(bco, reference):
    return Question.objects.get(catechism=bco, reference=reference)


def test_sections_carry_their_printed_reference(bco):
    assert bco.uses_native_references
    first = _section(bco, '1-1')
    assert first.display_number == '1-1'
    assert first.question_text == 'The Doctrine of Church Government'
    assert first.answer_text.startswith('The scriptural form of church government')
    assert _section(bco, 'Preface II').number == 2
    assert Question.objects.filter(catechism=bco).count() == bco.total_questions


def test_topics_are_titled_as_printed(bco):
    preface = Topic.objects.get(catechism=bco, slug='preface')
    assert preface.heading == 'Preface'
    assert (preface.display_start, preface.display_end) == ('Preface I', 'Preface III')

    chapter = _section(bco, '1-1').topic
    assert chapter.heading == 'Chapter 1: The Doctrine of Church Government'
    assert (chapter.display_start, chapter.display_end) == ('1-1', '1-7')


def test_other_confessions_still_number_by_chapter(db):
    from catechism.tests.conftest import CatechismFactory, QuestionFactory, TopicFactory
    wcf = CatechismFactory(document_type=Catechism.CONFESSION)
    topic = TopicFactory(catechism=wcf, order=3, name='Of God\'s Eternal Decree',
                         question_start=14, question_end=21)
    question = QuestionFactory(catechism=wcf, topic=topic, number=17)
    assert topic.heading == "Chapter 3: Of God's Eternal Decree"
    assert question.display_number == '3.4'
    assert (topic.display_start, topic.display_end) == ('3.1', '3.8')


def test_section_division_headings_title_their_section(bco):
    assert _section(bco, '5-1').question_text == 'A. Mission Churches'
    assert _section(bco, '21-4').question_text == 'Ordination Requirements and Procedures'
    assert _section(bco, '5-2').question_text == 'The Organization of a Particular Church'


def test_scripture_citations_load_as_proof_texts(bco):
    assert _section(bco, '56-5').get_proof_text_list() == ['Acts 2:39', 'Gen. 17:7', 'Acts 16:31']


def _make_legacy(bco):
    """Put the rows back the way the old loader left them: number in question_text."""
    titles = {v: k for k, v in load_pca_bco.LEGACY_PREFACE_TITLES.items()}
    for question in Question.objects.filter(catechism=bco):
        question.question_text = titles.get(question.reference, question.reference)
        question.reference = ''
        question.save()


@pytest.mark.django_db
def test_reload_keeps_readers_notes_on_the_same_section(bco):
    from accounts.models import MemorizationCard, ReadingPosition, UserNote
    from accounts.tests.conftest import UserFactory

    user = UserFactory()
    target = _section(bco, '47-1')
    preface = _section(bco, 'Preface II')
    note = UserNote.objects.create(user=user, question=target, text='mine')
    card = MemorizationCard.objects.create(user=user, question=preface)
    ReadingPosition.objects.create(user=user, catechism=bco, question=target)

    _make_legacy(bco)
    call_command('load_pca_bco', force=True)

    note.refresh_from_db()
    card.refresh_from_db()
    assert note.question.reference == '47-1'
    assert note.question.pk == target.pk
    assert card.question.reference == 'Preface II'
    assert ReadingPosition.objects.get(user=user).question.reference == '47-1'


@pytest.mark.django_db
def test_inserted_section_renumbers_without_losing_rows(bco, tmp_path, monkeypatch):
    """A new section (as 36-8 was in 2026) shifts every later sequential number."""
    from accounts.models import UserNote
    from accounts.tests.conftest import UserFactory

    target = _section(bco, '47-1')
    UserNote.objects.create(user=UserFactory(), question=target, text='mine')

    with open(DATA_PATH) as f:
        data = json.load(f)
    chapter_one = data['parts'][0]['chapters'][0]
    chapter_one['sections'].append({'number': '1-8', 'text': 'A new section.'})
    new_path = tmp_path / 'pca_bco.json'
    new_path.write_text(json.dumps(data))
    citations = Path(settings.BASE_DIR) / 'data' / 'pca-bco_proof_texts.json'
    monkeypatch.setattr(load_pca_bco, 'data_paths', lambda: (new_path, citations))

    call_command('load_pca_bco')

    moved = Question.objects.get(pk=target.pk)
    assert moved.reference == '47-1'
    assert moved.number == target.number + 1
    assert UserNote.objects.get().question_id == target.pk
    assert _section(bco, '1-8').topic == _section(bco, '1-1').topic
    bco.refresh_from_db()
    assert bco.total_questions == Question.objects.filter(catechism=bco).count()


@pytest.mark.django_db
def test_crossrefs_rebuild_and_drop_stale_links(bco):
    call_command('load_catechism')
    call_command('load_wlc')
    call_command('load_wcf')
    call_command('load_bco_crossrefs')
    count = StandardCrossReference.objects.filter(source_question__catechism=bco).count()
    assert count

    # A link no mapping produces is removed on the next rebuild.
    stray = StandardCrossReference.objects.create(
        source_question=_section(bco, '20-1'),
        target_question=Question.objects.get(catechism__slug='wsc', number=1),
    )
    call_command('load_bco_crossrefs', force=True)
    assert not StandardCrossReference.objects.filter(pk=stray.pk).exists()
    assert StandardCrossReference.objects.filter(source_question__catechism=bco).count() == count

    # Reloading the BCO in place leaves the links attached.
    call_command('load_pca_bco', force=True)
    assert StandardCrossReference.objects.filter(source_question__catechism=bco).count() == count


# ── Citations and pages ─────────────────────────────────────────────────


def test_citations_use_the_printed_reference(bco):
    section = _section(bco, '21-4')
    assert citation_label(section) == 'BCO 21-4'
    assert reference_slug(section) == '21-4'
    assert resolve_reference(bco, '21-4') == section
    assert resolve_reference(bco, '21.4') == section
    assert resolve_reference(bco, 'Preface II') == _section(bco, 'Preface II')
    assert resolve_reference(bco, 'preface-ii') == _section(bco, 'Preface II')
    assert resolve_reference(bco, '99-9') is None
    assert reference_slug(_section(bco, 'Preface II')) == 'preface-ii'


def test_cite_permalink_redirects_to_the_section(client, bco):
    section = _section(bco, '36-8')
    response = client.get('/cite/pca-bco/36-8/')
    assert response.status_code == 301
    assert response['Location'] == section.get_absolute_url()


def test_section_page_shows_the_printed_reference(client, bco):
    section = _section(bco, '12-5')
    response = client.get(section.get_absolute_url())
    html = response.content.decode()
    assert response.status_code == 200
    assert 'Cite BCO 12-5' in html
    assert 'Chapter 12: The Church Session' in html
    assert 'Chapter 13: Chapter 12' not in html
    assert reverse('catechism:citation_permalink', kwargs={
        'catechism_slug': 'pca-bco', 'reference': '12-5'}) in html
    assert '<p>a. To inquire into the knowledge' in html


def test_format_paragraphs_does_not_treat_abbreviations_as_headings():
    html = format_paragraphs('Members of the PCA.\n\na. One; <b>\nb. Two.')
    assert html == '<p>Members of the PCA.</p><p>a. One; &lt;b&gt; b. Two.</p>'


# ── Update check ────────────────────────────────────────────────────────


def test_update_check_reads_the_english_pdf_link():
    page = '''
        <a href="https://www.pcaac.org/wp-content/uploads/2026/08/2026-KBCO-ALL.pdf">Korean</a>
        <a id="BCODOWNLOAD" href="https://www.pcaac.org/wp-content/uploads/2026/07/BCO_2026.pdf">BCO</a>
        <a href="https://www.pcaac.org/wp-content/uploads/2025/09/LDO_2025.pdf">Spanish</a>
    '''
    assert current_pdf_url(page) == 'https://www.pcaac.org/wp-content/uploads/2026/07/BCO_2026.pdf'
    assert current_pdf_url('<p>no links</p>') is None
