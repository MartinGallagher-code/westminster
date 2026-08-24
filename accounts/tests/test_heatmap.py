"""Practice made visible: per-day counts and the calendar grid."""

from datetime import date, timedelta

import pytest
from django.contrib.auth.models import User

from accounts.models import MemorizationCard, ReviewDay
from accounts.views import _practice_heatmap
from catechism.models import Catechism
from catechism.tests.conftest import QuestionFactory, TopicFactory

TODAY = date(2026, 8, 23)


@pytest.fixture
def learner(db):
    return User.objects.create_user(username='learner', password='catechism-1647')


@pytest.mark.django_db
def test_recording_counts_reviews_per_day(learner):
    ReviewDay.record(learner, TODAY)
    ReviewDay.record(learner, TODAY)
    ReviewDay.record(learner, TODAY - timedelta(days=1))

    assert ReviewDay.objects.get(user=learner, day=TODAY).reviews == 2
    assert ReviewDay.objects.get(user=learner, day=TODAY - timedelta(days=1)).reviews == 1


@pytest.mark.django_db
def test_the_grid_is_whole_weeks_starting_on_monday(learner):
    heatmap = _practice_heatmap(learner, TODAY)
    assert all(len(week) == 7 for week in heatmap['weeks'])
    assert heatmap['weeks'][0][0]['day'].weekday() == 0


@pytest.mark.django_db
def test_busier_days_reach_a_higher_level(learner):
    ReviewDay.objects.create(user=learner, day=TODAY, reviews=40)
    ReviewDay.objects.create(user=learner, day=TODAY - timedelta(days=1), reviews=1)

    days = {d['day']: d for week in _practice_heatmap(learner, TODAY)['weeks'] for d in week}
    assert days[TODAY]['level'] == 4
    assert 0 < days[TODAY - timedelta(days=1)]['level'] < 4


@pytest.mark.django_db
def test_days_without_practice_are_level_zero(learner):
    days = {d['day']: d for week in _practice_heatmap(learner, TODAY)['weeks'] for d in week}
    assert days[TODAY]['level'] == 0


@pytest.mark.django_db
def test_days_after_today_are_marked_future(learner):
    heatmap = _practice_heatmap(learner, TODAY)
    future = [d for week in heatmap['weeks'] for d in week if d['day'] > TODAY]
    assert all(d['future'] for d in future)


@pytest.mark.django_db
def test_reviewing_shows_up_on_the_deck_page(client, learner):
    catechism = Catechism.objects.get(slug='wsc')
    topic = TopicFactory(catechism=catechism, question_start=1, question_end=1)
    question = QuestionFactory(catechism=catechism, topic=topic, number=1)
    card = MemorizationCard.objects.create(user=learner, question=question)

    client.force_login(learner)
    client.post('/accounts/memorize/review/', {'card': card.pk, 'grade': 'good'})

    body = client.get('/accounts/memorize/').content.decode()
    assert 'practice-heatmap' in body
    assert ReviewDay.objects.filter(user=learner).count() == 1
