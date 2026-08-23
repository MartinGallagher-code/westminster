"""The data-integrity command that guards the loaded corpus."""

import pytest
from django.core.management import CommandError, call_command

from catechism.models import Catechism
from .conftest import CatechismFactory, QuestionFactory, TopicFactory


@pytest.mark.django_db
def test_reports_missing_westminster_documents():
    """An empty database is not silently 'fine'."""
    with pytest.raises(CommandError) as exc:
        call_command('check_site_integrity')
    assert 'integrity check' in str(exc.value)


@pytest.mark.django_db
def test_flags_a_document_that_no_view_can_reach(catechism, confession):
    """The bug that hid five confessions for good: questions behind
    tradition='other', which every view gates off."""
    stranded = CatechismFactory(
        name='Savoy Declaration', abbreviation='Savoy', slug='savoy',
        total_questions=1, tradition=Catechism.OTHER,
        document_type=Catechism.CONFESSION,
    )
    topic = TopicFactory(catechism=stranded, question_start=1, question_end=1)
    QuestionFactory(catechism=stranded, topic=topic, number=1)

    with pytest.raises(CommandError):
        call_command('check_site_integrity')


@pytest.mark.django_db
def test_systematic_theologies_are_not_flagged(catechism):
    """Calvin's Institutes and Hodge's Outlines are reference works, not
    confessions in a collection; tradition='other' is correct for them."""
    from catechism.management.commands import check_site_integrity

    reference_work = CatechismFactory(
        name="Calvin's Institutes", abbreviation='Inst', slug='institutes',
        total_questions=1, tradition=Catechism.OTHER,
        document_type=Catechism.SYSTEMATIC_THEOLOGY,
    )
    topic = TopicFactory(catechism=reference_work, question_start=1, question_end=1)
    QuestionFactory(catechism=reference_work, topic=topic, number=1)

    command = check_site_integrity.Command()
    command.failures = []
    command.stdout = type('Sink', (), {'write': lambda self, msg: None})()
    command._check_documents_loaded()

    assert not any('Inst' in failure for failure in command.failures)
