"""The printable small-group session handout."""

import pytest

from catechism.handout import build_item, discussion_prompts
from catechism.models import ScripturePassage, StandardCrossReference, Topic
from .conftest import CommentaryFactory, CommentarySourceFactory, QuestionFactory


@pytest.fixture
def proofed_question(question):
    question.proof_texts = 'Rom 8:30; 1 Cor 13:12'
    question.save()
    ScripturePassage.objects.create(
        reference='Rom 8:30', text='Whom he did predestinate, them he also called…',
    )
    return question


@pytest.mark.django_db
def test_handout_lists_proof_texts_with_their_loaded_text(proofed_question):
    item = build_item(proofed_question)
    references = [proof['reference'] for proof in item['proofs']]
    assert references == ['Rom 8:30', '1 Cor 13:12']
    assert item['proofs'][0]['text'].startswith('Whom he did predestinate')
    # A reference with no loaded passage still appears, without text.
    assert item['proofs'][1]['text'] == ''


@pytest.mark.django_db
def test_prompts_are_built_from_this_passage_not_boilerplate(proofed_question):
    item = build_item(proofed_question)
    assert item['prompts']
    assert any('Rom 8:30' in prompt for prompt in item['prompts'])


@pytest.mark.django_db
def test_a_bare_question_still_gets_one_usable_prompt(question):
    prompts = discussion_prompts(question, [], [], [])
    assert len(prompts) == 1
    assert 'your own words' in prompts[0]


@pytest.mark.django_db
def test_cross_references_become_read_alongside_prompts(catechism, topic, question):
    other = QuestionFactory(
        catechism=catechism, topic=topic, number=42, question_text='A parallel treatment',
    )
    StandardCrossReference.objects.create(source_question=question, target_question=other)

    item = build_item(question)
    assert other in item['cross_references']
    assert any('treats the same ground' in prompt for prompt in item['prompts'])


@pytest.mark.django_db
def test_leader_notes_are_attributed_and_trimmed(question):
    source = CommentarySourceFactory(name="Fisher's Catechism", author='James Fisher')
    CommentaryFactory(question=question, source=source, body=' '.join(['word'] * 400))

    notes = build_item(question)['leader_notes']
    assert notes[0]['source'] == "Fisher's Catechism"
    assert notes[0]['author'] == 'James Fisher'
    assert len(notes[0]['body'].split()) <= 121      # trimmed, with an ellipsis
    assert notes[0]['body'].endswith('…')


@pytest.mark.django_db
def test_handout_page_for_a_single_question(client, catechism, proofed_question):
    resp = client.get('/handout/wsc/1/')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert proofed_question.question_text in body
    assert 'For discussion' in body
    assert 'Rom 8:30' in body
    assert 'Print or save as PDF' in body


@pytest.mark.django_db
def test_handout_page_for_a_whole_chapter(client, confession):
    chapter = Topic.objects.create(
        catechism=confession, name='Of the Holy Scripture', slug='of-the-holy-scripture',
        order=1, question_start=1, question_end=2,
    )
    QuestionFactory(catechism=confession, topic=chapter, number=1, question_text='First section')
    QuestionFactory(catechism=confession, topic=chapter, number=2, question_text='Second section')

    resp = client.get('/handout/wcf/topic/of-the-holy-scripture/')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert 'First section' in body and 'Second section' in body
    assert 'Of the Holy Scripture' in body


@pytest.mark.django_db
def test_unknown_handout_references_are_404(client, catechism):
    assert client.get('/handout/wsc/999/').status_code == 404
    assert client.get('/handout/nope/1/').status_code == 404
    assert client.get('/handout/wsc/topic/nope/').status_code == 404


@pytest.mark.django_db
def test_question_and_topic_pages_link_to_the_handout(client, catechism, topic, question):
    assert '/handout/wsc/1/' in client.get('/wsc/questions/1/').content.decode()
    body = client.get(topic.get_absolute_url()).content.decode()
    assert f'/handout/wsc/topic/{topic.slug}/' in body
