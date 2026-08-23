"""Memorisation deck: scheduling maths and the review flow."""

from datetime import date, timedelta

import pytest
from django.contrib.auth.models import User

from accounts import scheduling
from accounts.models import MemorizationCard
from accounts.scheduling import AGAIN, EASY, GOOD, HARD
from catechism.models import Catechism
from catechism.tests.conftest import QuestionFactory, TopicFactory


TODAY = date(2026, 1, 1)


# ── scheduling (pure functions, no database) ──────────────────────────────


def test_first_three_reviews_follow_the_classic_intervals():
    reps, interval, ease = 0, 0, scheduling.DEFAULT_EASE
    seen = []
    for _ in range(3):
        reps, interval, ease, _due = scheduling.review(reps, interval, ease, GOOD, TODAY)
        seen.append(interval)
    assert seen == [1, 6, 15]


def test_forgetting_sends_the_card_back_to_tomorrow():
    reps, interval, ease, due = scheduling.review(5, 90, 2.5, AGAIN, TODAY)
    assert reps == 0
    assert interval == 1
    assert due == TODAY + timedelta(days=1)


def test_forgetting_lowers_the_ease_but_does_not_reset_it():
    _reps, _interval, ease, _due = scheduling.review(5, 90, 2.5, AGAIN, TODAY)
    assert scheduling.MIN_EASE < ease < 2.5


def test_ease_never_falls_below_the_floor():
    ease = scheduling.DEFAULT_EASE
    for _ in range(20):
        ease = scheduling.next_ease(ease, AGAIN)
    assert ease == scheduling.MIN_EASE


def test_hard_grows_more_slowly_than_good_and_easy_fastest():
    hard = scheduling.review(3, 10, 2.5, HARD, TODAY)[1]
    good = scheduling.review(3, 10, 2.5, GOOD, TODAY)[1]
    easy = scheduling.review(3, 10, 2.5, EASY, TODAY)[1]
    assert hard < good < easy


def test_intervals_are_capped():
    assert scheduling.review(20, 10**6, 2.5, EASY, TODAY)[1] == scheduling.MAX_INTERVAL_DAYS


def test_unknown_grade_is_rejected():
    with pytest.raises(ValueError):
        scheduling.review(0, 0, 2.5, 'excellent', TODAY)


# ── the deck ──────────────────────────────────────────────────────────────


@pytest.fixture
def learner(db):
    return User.objects.create_user(username='learner', password='catechism-1647')


@pytest.fixture
def wsc_question(db):
    # The WSC row is seeded by migration 0004; reuse it rather than creating a
    # second one, which trips the unique slug constraint.
    catechism = Catechism.objects.get(slug='wsc')
    catechism.total_questions = 2
    catechism.save()
    topic = TopicFactory(catechism=catechism, question_start=1, question_end=2)
    return QuestionFactory(
        catechism=catechism, topic=topic, number=1,
        question_text='What is the chief end of man?',
        answer_text="Man's chief end is to glorify God, and to enjoy him for ever.",
    )


@pytest.mark.django_db
def test_a_new_card_is_due_immediately(learner, wsc_question):
    card = MemorizationCard.objects.create(user=learner, question=wsc_question)
    assert card.is_new
    assert card.is_due()


@pytest.mark.django_db
def test_reviewing_advances_the_schedule_and_records_the_lapse(learner, wsc_question):
    card = MemorizationCard.objects.create(user=learner, question=wsc_question)
    card.apply_review(GOOD, TODAY)
    card.apply_review(GOOD, TODAY)
    assert card.repetitions == 2
    assert card.lapses == 0

    card.apply_review(AGAIN, TODAY)
    card.refresh_from_db()
    assert card.repetitions == 0
    assert card.lapses == 1


@pytest.mark.django_db
def test_a_long_interval_counts_as_known(learner, wsc_question):
    card = MemorizationCard.objects.create(user=learner, question=wsc_question)
    card.interval_days = scheduling.MATURE_INTERVAL_DAYS
    assert card.is_mature


@pytest.mark.django_db
def test_deck_page_requires_login(client):
    resp = client.get('/accounts/memorize/')
    assert resp.status_code == 302
    assert '/accounts/login/' in resp['Location']


@pytest.mark.django_db
def test_adding_and_removing_a_single_answer(client, learner, wsc_question):
    client.force_login(learner)

    client.post(f'/accounts/memorize/add/{wsc_question.pk}/')
    assert MemorizationCard.objects.filter(user=learner, question=wsc_question).exists()

    # Adding twice is not an error and does not duplicate the card.
    client.post(f'/accounts/memorize/add/{wsc_question.pk}/')
    assert MemorizationCard.objects.filter(user=learner).count() == 1

    client.post(f'/accounts/memorize/remove/{wsc_question.pk}/')
    assert not MemorizationCard.objects.filter(user=learner).exists()


@pytest.mark.django_db
def test_adding_a_whole_catechism(client, learner, wsc_question):
    QuestionFactory(
        catechism=wsc_question.catechism, topic=wsc_question.topic, number=2,
    )
    client.force_login(learner)
    client.post('/accounts/memorize/add-document/', {'catechism': 'wsc'})
    assert MemorizationCard.objects.filter(user=learner).count() == 2

    # Adding again adds nothing rather than failing on the unique constraint.
    client.post('/accounts/memorize/add-document/', {'catechism': 'wsc'})
    assert MemorizationCard.objects.filter(user=learner).count() == 2


@pytest.mark.django_db
def test_review_shows_a_due_card_and_grading_reschedules_it(client, learner, wsc_question):
    card = MemorizationCard.objects.create(user=learner, question=wsc_question)
    client.force_login(learner)

    resp = client.get('/accounts/memorize/review/')
    assert resp.status_code == 200
    assert 'chief end of man' in resp.content.decode()

    resp = client.post('/accounts/memorize/review/', {'card': card.pk, 'grade': GOOD})
    assert resp.status_code == 302
    card.refresh_from_db()
    assert card.repetitions == 1
    assert card.due_on > card.created_at.date()


@pytest.mark.django_db
def test_review_redirects_home_when_nothing_is_due(client, learner):
    client.force_login(learner)
    resp = client.get('/accounts/memorize/review/')
    assert resp.status_code == 302
    assert resp['Location'] == '/accounts/memorize/'


@pytest.mark.django_db
def test_a_reader_cannot_grade_someone_elses_card(client, learner, wsc_question):
    other = User.objects.create_user(username='someone-else', password='catechism-1647')
    card = MemorizationCard.objects.create(user=other, question=wsc_question)

    client.force_login(learner)
    resp = client.post('/accounts/memorize/review/', {'card': card.pk, 'grade': GOOD})
    assert resp.status_code == 404
    card.refresh_from_db()
    assert card.repetitions == 0


@pytest.mark.django_db
def test_an_unknown_grade_is_rejected_by_the_view(client, learner, wsc_question):
    card = MemorizationCard.objects.create(user=learner, question=wsc_question)
    client.force_login(learner)
    client.post('/accounts/memorize/review/', {'card': card.pk, 'grade': 'nonsense'})
    card.refresh_from_db()
    assert card.repetitions == 0
