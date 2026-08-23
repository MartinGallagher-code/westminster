"""Checking the loaded text against an independent transcription."""

import pytest
from django.core.management import CommandError, call_command

from catechism.management.commands.check_transcription import (
    normalise, similarity, word_pairs,
)
from catechism.models import Catechism
from .conftest import QuestionFactory, TopicFactory


def test_normalise_folds_typesetting_not_wording():
    assert normalise('Man’s chief end') == normalise("Man's chief end")
    assert normalise('for ever—and ever') == normalise('for ever - and ever')
    assert normalise('  Glorify   GOD.  ') == 'glorify god'


def test_identical_wording_scores_one():
    assert similarity('to glorify God', 'To glorify God!') == 1.0


def test_a_changed_word_lowers_the_score():
    assert similarity('to glorify God', 'to glorify grace') < 1.0


def test_word_pairs_report_both_sides():
    pairs = word_pairs('maintain piety justice', 'maintain justice')
    assert ('piety', '—') in pairs


def test_word_pairs_mark_an_addition():
    pairs = word_pairs('the rule', 'the only rule')
    assert ('—', 'only') in pairs


@pytest.fixture
def wsc_matching_the_reference(db):
    """WSC 1 transcribed exactly as the Atlas has it."""
    from westminster_standards.works import get_work_by_slug

    reference = get_work_by_slug('wsc')['questions'][0]
    catechism = Catechism.objects.get(slug='wsc')
    catechism.total_questions = 1
    catechism.save()
    topic = TopicFactory(catechism=catechism, question_start=1, question_end=1)
    return QuestionFactory(
        catechism=catechism, topic=topic, number=1,
        question_text=reference['question'], answer_text=reference['answer'],
    )


@pytest.mark.django_db
def test_matching_transcriptions_report_agreement(wsc_matching_the_reference, capsys):
    call_command('check_transcription', document='wsc')
    assert 'agree everywhere checked' in capsys.readouterr().out


@pytest.mark.django_db
def test_a_divergence_is_reported_with_both_readings(wsc_matching_the_reference, capsys):
    question = wsc_matching_the_reference
    question.answer_text = question.answer_text.replace('glorify', 'magnify')
    question.save()

    call_command('check_transcription', document='wsc')
    output = capsys.readouterr().out
    assert 'WSC 1' in output
    assert 'magnify' in output and 'glorify' in output


@pytest.mark.django_db
def test_summary_groups_by_the_differing_words(wsc_matching_the_reference, capsys):
    question = wsc_matching_the_reference
    question.answer_text = question.answer_text.replace('glorify', 'magnify')
    question.save()

    call_command('check_transcription', document='wsc', summary=True)
    output = capsys.readouterr().out
    assert 'distinct differences' in output
    assert 'magnify' in output


@pytest.mark.django_db
def test_fail_on_divergence_exits_non_zero(wsc_matching_the_reference):
    question = wsc_matching_the_reference
    question.answer_text = 'Something else entirely.'
    question.save()

    with pytest.raises(CommandError):
        call_command('check_transcription', document='wsc', fail_on_divergence=True)


@pytest.mark.django_db
def test_an_empty_document_is_not_an_error(db, capsys):
    call_command('check_transcription', document='wlc')
    assert 'compared 0' in capsys.readouterr().out
