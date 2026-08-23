"""Tools for a group: the presenter view and the session planner."""

import pytest

from catechism.models import Topic
from .conftest import QuestionFactory


@pytest.fixture
def wsc_topic(catechism):
    catechism.total_questions = 3
    catechism.save()
    topic = Topic.objects.create(
        catechism=catechism, name='Of God', slug='of-god',
        order=1, question_start=1, question_end=3,
    )
    for number in (1, 2, 3):
        QuestionFactory(
            catechism=catechism, topic=topic, number=number,
            question_text=f'Question {number}?', answer_text=f'Answer {number}.',
        )
    return topic


@pytest.mark.django_db
def test_presenter_shows_every_question_as_a_slide(client, wsc_topic):
    resp = client.get('/present/wsc/topic/of-god/')
    assert resp.status_code == 200
    assert len(resp.context['slides']) == 3
    body = resp.content.decode()
    assert 'presenter-slide' in body
    assert 'Question 1?' in body and 'Question 3?' in body


@pytest.mark.django_db
def test_the_presenter_hides_the_site_chrome(client, wsc_topic):
    """A group is looking at this from across a room."""
    body = client.get('/present/wsc/topic/of-god/').content.decode()
    assert 'presenter-bar' in body
    assert 'class="presenter"' in body or 'presenter' in body


@pytest.mark.django_db
def test_answers_start_hidden_so_the_leader_can_ask_first(client, wsc_topic):
    body = client.get('/present/wsc/topic/of-god/').content.decode()
    assert 'data-answer hidden' in body


@pytest.mark.django_db
def test_presenting_an_explicit_range(client, wsc_topic):
    resp = client.get('/present/wsc/?from=1&to=2')
    assert [slide['question'] for slide in resp.context['slides']] == ['Question 1?', 'Question 2?']


@pytest.mark.django_db
def test_presenting_nothing_is_a_404(client, wsc_topic):
    assert client.get('/present/wsc/?from=90&to=99').status_code == 404
    assert client.get('/present/wsc/topic/nope/').status_code == 404


@pytest.mark.django_db
def test_the_planner_asks_for_a_document_first(client, wsc_topic):
    resp = client.get('/plan/')
    assert resp.status_code == 200
    assert 'plan' not in resp.context or not resp.context.get('plan')


@pytest.mark.django_db
def test_the_planner_offers_everything_for_a_chosen_section(client, wsc_topic):
    resp = client.get('/plan/?catechism=wsc&topic=of-god')
    plan = resp.context['plan']

    assert plan['reading'] == wsc_topic.get_absolute_url()
    assert plan['handout'] == '/handout/wsc/topic/of-god/'
    assert plan['presenter'] == '/present/wsc/topic/of-god/'
    assert len(resp.context['questions']) == 3


@pytest.mark.django_db
def test_the_plan_is_shareable(client, wsc_topic):
    body = client.get('/plan/?catechism=wsc&topic=of-god').content.decode()
    assert 'data-copy="url"' in body


@pytest.mark.django_db
def test_an_unknown_selection_does_not_error(client, wsc_topic):
    assert client.get('/plan/?catechism=nope&topic=nope').status_code == 200
    assert client.get('/plan/?catechism=wsc&topic=nope').status_code == 200


@pytest.mark.django_db
def test_topic_pages_offer_to_present(client, wsc_topic):
    body = client.get(wsc_topic.get_absolute_url()).content.decode()
    assert '/present/wsc/topic/of-god/' in body
