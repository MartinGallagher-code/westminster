"""Drill modes: first letters, gaps, and typing it out."""

from datetime import date, timedelta

import pytest
from django.contrib.auth.models import User

from accounts import drills
from accounts.models import MemorizationCard, UserProfile
from catechism.models import Catechism
from catechism.tests.conftest import QuestionFactory, TopicFactory

ANSWER = "Man's chief end is to glorify God, and to enjoy him for ever."


# ── first letters ─────────────────────────────────────────────────────────


def test_first_letters_keeps_the_shape_of_the_sentence():
    result = drills.first_letters('Man is to glorify God')
    assert result == 'M__ i_ t_ g______ G__'


def test_first_letters_keeps_punctuation_as_a_cue():
    assert drills.first_letters('God, and man.') == 'G__, a__ m__.'


def test_first_letters_of_nothing_is_nothing():
    assert drills.first_letters('') == ''
    assert drills.first_letters(None) == ''


# ── gaps ──────────────────────────────────────────────────────────────────


def test_cloze_blanks_some_words_but_not_all():
    tokens = drills.cloze(ANSWER, seed=1)
    blanks = [t for t in tokens if t['blank']]
    assert 0 < len(blanks) < len(tokens)


def test_cloze_is_stable_for_the_same_seed():
    """A drill that reshuffles when the page reloads is a different drill."""
    first = drills.cloze(ANSWER, seed=42)
    second = drills.cloze(ANSWER, seed=42)
    assert first == second
    assert drills.cloze(ANSWER, seed=43) != first


def test_cloze_leaves_short_words_alone():
    """Blanking "of" teaches nothing."""
    for token in drills.cloze(ANSWER, seed=5):
        if token['blank']:
            assert len(token['text'].strip('.,;')) >= drills.MIN_CLOZE_WORD_LENGTH


def test_cloze_of_only_short_words_blanks_nothing():
    tokens = drills.cloze('it is of us', seed=1)
    assert not any(token['blank'] for token in tokens)


# ── typing ────────────────────────────────────────────────────────────────


def test_typing_it_perfectly_scores_full_marks():
    result = drills.score_typed(ANSWER, ANSWER)
    assert result['percentage'] == 100
    assert result['is_perfect']
    assert all(word['status'] == 'correct' for word in result['marked'])


def test_punctuation_and_case_are_forgiven():
    result = drills.score_typed(ANSWER, ANSWER.lower().replace(',', '').replace('.', ''))
    assert result['is_perfect']


def test_a_missing_word_is_marked_missing():
    result = drills.score_typed('to glorify God and enjoy him', 'to glorify God enjoy him')
    statuses = {word['text']: word['status'] for word in result['marked']}
    assert statuses['and'] == 'missing'
    assert result['percentage'] < 100


def test_a_wrong_word_is_marked_and_the_intruder_reported():
    result = drills.score_typed('to glorify God', 'to magnify God')
    statuses = {word['text']: word['status'] for word in result['marked']}
    assert statuses['glorify'] == 'wrong'
    assert 'magnify' in result['extras']


def test_typing_nothing_scores_nothing():
    result = drills.score_typed(ANSWER, '')
    assert result['percentage'] == 0
    assert not result['is_perfect']


def test_padding_the_answer_does_not_inflate_the_score():
    """Typing the answer plus a paragraph of guesses is not a perfect recall."""
    result = drills.score_typed('to glorify God', 'to glorify God ' + 'and much more besides')
    assert result['percentage'] < 100


@pytest.mark.parametrize('accuracy,expected', [
    (1.0, 'easy'),
    (0.95, 'good'),
    (0.75, 'hard'),
    (0.10, 'again'),
])
def test_suggested_grade_tracks_accuracy(accuracy, expected):
    assert drills.suggested_grade(accuracy) == expected


# ── the review flow ───────────────────────────────────────────────────────


@pytest.fixture
def learner(db):
    return User.objects.create_user(username='learner', password='catechism-1647')


@pytest.fixture
def card(db, learner):
    catechism = Catechism.objects.get(slug='wsc')
    catechism.total_questions = 1
    catechism.save()
    topic = TopicFactory(catechism=catechism, question_start=1, question_end=1)
    question = QuestionFactory(
        catechism=catechism, topic=topic, number=1,
        question_text='What is the chief end of man?', answer_text=ANSWER,
    )
    return MemorizationCard.objects.create(user=learner, question=question)


@pytest.mark.django_db
@pytest.mark.parametrize('mode', ['recall', 'initials', 'cloze', 'type'])
def test_every_drill_mode_renders(client, learner, card, mode):
    client.force_login(learner)
    resp = client.get(f'/accounts/memorize/review/?mode={mode}')
    assert resp.status_code == 200
    assert resp.context['mode'] == mode


@pytest.mark.django_db
def test_an_unknown_mode_falls_back_to_reading(client, learner, card):
    client.force_login(learner)
    resp = client.get('/accounts/memorize/review/?mode=telepathy')
    assert resp.context['mode'] == 'recall'


@pytest.mark.django_db
def test_the_answer_is_not_in_the_page_before_it_is_earned(client, learner, card):
    """First letters must not ship the full text in the markup."""
    client.force_login(learner)
    body = client.get('/accounts/memorize/review/?mode=initials').content.decode()
    assert 'M__' in body


@pytest.mark.django_db
def test_typing_an_answer_is_checked_and_a_grade_suggested(client, learner, card):
    client.force_login(learner)
    resp = client.post('/accounts/memorize/review/', {
        'card': card.pk, 'mode': 'type', 'action': 'check', 'typed': ANSWER,
    })
    assert resp.status_code == 200
    assert resp.context['result']['is_perfect']
    assert resp.context['suggested_grade'] == 'easy'
    # Checking is not reviewing: the schedule has not moved yet.
    card.refresh_from_db()
    assert card.repetitions == 0


@pytest.mark.django_db
def test_grading_keeps_the_chosen_mode(client, learner, card):
    client.force_login(learner)
    resp = client.post('/accounts/memorize/review/', {
        'card': card.pk, 'mode': 'cloze', 'grade': 'good',
    })
    assert resp.status_code == 302
    assert 'mode=cloze' in resp['Location']


# ── streak ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_reviewing_starts_a_streak(client, learner, card):
    client.force_login(learner)
    client.post('/accounts/memorize/review/', {'card': card.pk, 'grade': 'good'})

    profile = UserProfile.objects.get(user=learner)
    assert profile.review_streak == 1
    assert profile.total_reviews == 1


@pytest.mark.django_db
def test_a_streak_counts_days_not_reviews(learner):
    profile = UserProfile.objects.get(user=learner)
    today = date(2026, 8, 23)
    profile.record_review(today)
    profile.record_review(today)
    assert profile.review_streak == 1
    assert profile.total_reviews == 2


@pytest.mark.django_db
def test_a_streak_grows_on_consecutive_days(learner):
    profile = UserProfile.objects.get(user=learner)
    start = date(2026, 8, 20)
    for offset in range(4):
        profile.record_review(start + timedelta(days=offset))
    assert profile.review_streak == 4
    assert profile.longest_streak == 4


@pytest.mark.django_db
def test_a_missed_day_restarts_the_streak_but_not_the_record(learner):
    profile = UserProfile.objects.get(user=learner)
    start = date(2026, 8, 1)
    for offset in range(5):
        profile.record_review(start + timedelta(days=offset))
    profile.record_review(start + timedelta(days=10))

    assert profile.review_streak == 1
    assert profile.longest_streak == 5
