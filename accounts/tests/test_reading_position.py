"""Remembering where a reader was, and offering it back."""

import pytest
from django.contrib.auth.models import User

from accounts.models import MemorizationCard, ReadingPosition
from catechism.models import Catechism
from catechism.tests.conftest import QuestionFactory, TopicFactory


@pytest.fixture
def reader(db):
    return User.objects.create_user(username='reader', password='catechism-1647')


@pytest.fixture
def questions(db):
    catechism = Catechism.objects.get(slug='wsc')
    catechism.total_questions = 3
    catechism.save()
    topic = TopicFactory(catechism=catechism, question_start=1, question_end=3)
    return [
        QuestionFactory(catechism=catechism, topic=topic, number=n)
        for n in (1, 2, 3)
    ]


@pytest.mark.django_db
def test_reading_a_question_records_the_position(client, reader, questions):
    client.force_login(reader)
    client.get(questions[1].get_absolute_url())

    position = ReadingPosition.objects.get(user=reader)
    assert position.question == questions[1]


@pytest.mark.django_db
def test_only_the_latest_position_is_kept_per_document(client, reader, questions):
    client.force_login(reader)
    for question in questions:
        client.get(question.get_absolute_url())

    assert ReadingPosition.objects.filter(user=reader).count() == 1
    assert ReadingPosition.objects.get(user=reader).question == questions[-1]


@pytest.mark.django_db
def test_anonymous_reading_is_not_recorded(client, questions):
    client.get(questions[0].get_absolute_url())
    assert not ReadingPosition.objects.exists()


@pytest.mark.django_db
def test_readers_do_not_see_each_others_positions(client, reader, questions):
    other = User.objects.create_user(username='other', password='catechism-1647')
    ReadingPosition.objects.create(
        user=other, catechism=questions[0].catechism, question=questions[2],
    )

    client.force_login(reader)
    client.get(questions[0].get_absolute_url())
    resp = client.get('/')
    positions = resp.context['reading_positions']
    assert [p.user for p in positions] == [reader]


@pytest.mark.django_db
def test_the_home_page_offers_the_way_back(client, reader, questions):
    client.force_login(reader)
    client.get(questions[1].get_absolute_url())

    body = client.get('/').content.decode()
    assert 'Pick up where you left off' in body
    assert questions[1].get_absolute_url() in body


@pytest.mark.django_db
def test_the_strip_reports_what_is_due(client, reader, questions):
    MemorizationCard.objects.create(user=reader, question=questions[0])
    client.force_login(reader)

    resp = client.get('/')
    assert resp.context['memorisation_due'] == 1
    assert 'due today' in resp.content.decode()


@pytest.mark.django_db
def test_signed_out_visitors_see_no_strip(client, questions):
    assert 'Pick up where you left off' not in client.get('/').content.decode()
