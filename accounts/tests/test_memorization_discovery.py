"""Finding the memorisation deck in the first place.

It shipped behind a login wall with its only entry point a navbar link that
signed-out visitors never saw, so nobody who did not already know about it
could find it.
"""

import pytest
from django.contrib.auth.models import User

from accounts.models import MemorizationCard
from catechism.models import Catechism
from catechism.tests.conftest import QuestionFactory, TopicFactory


@pytest.fixture
def learner(db):
    return User.objects.create_user(username='learner', password='catechism-1647')


@pytest.fixture
def wsc_topic(db):
    catechism = Catechism.objects.get(slug='wsc')
    catechism.total_questions = 2
    catechism.save()
    topic = TopicFactory(
        catechism=catechism, name='Of God', slug='of-god',
        question_start=1, question_end=2,
    )
    QuestionFactory(catechism=catechism, topic=topic, number=1)
    QuestionFactory(catechism=catechism, topic=topic, number=2)
    return topic


@pytest.mark.django_db
def test_signed_out_visitors_get_an_explanation_not_a_login_wall(client):
    resp = client.get('/accounts/memorize/')

    assert resp.status_code == 200, 'the deck page should explain itself, not redirect'
    body = resp.content.decode()
    assert 'Create an account' in body
    assert 'just before you would forget it' in body


@pytest.mark.django_db
def test_the_navbar_offers_it_to_everyone(client, wsc_topic):
    signed_out = client.get('/').content.decode()
    assert '/accounts/memorize/' in signed_out


@pytest.mark.django_db
def test_the_home_page_advertises_it(client, wsc_topic):
    body = client.get('/').content.decode()
    assert 'Memorise the Catechism' in body


@pytest.mark.django_db
def test_the_study_desk_links_to_the_deck(client, learner):
    client.force_login(learner)
    body = client.get('/accounts/dashboard/').content.decode()
    assert 'Memorisation deck' in body
    assert 'Start memorising' in body


@pytest.mark.django_db
def test_the_study_desk_shows_what_is_due(client, learner, wsc_topic):
    MemorizationCard.objects.create(
        user=learner, question=wsc_topic.questions.first(),
    )
    client.force_login(learner)
    resp = client.get('/accounts/dashboard/')

    assert resp.context['memorisation_total'] == 1
    assert resp.context['memorisation_due'] == 1
    assert 'Review now' in resp.content.decode()


@pytest.mark.django_db
def test_a_catechism_page_offers_to_memorise_the_whole_document(client, wsc_topic):
    body = client.get('/wsc/').content.decode()
    assert 'Memorise this catechism' in body


@pytest.mark.django_db
def test_a_topic_page_offers_to_memorise_that_topic(client, wsc_topic):
    body = client.get(wsc_topic.get_absolute_url()).content.decode()
    assert 'Memorise this topic' in body


@pytest.mark.django_db
def test_adding_a_topic_adds_every_answer_under_it(client, learner, wsc_topic):
    client.force_login(learner)
    resp = client.post(f'/accounts/memorize/add-topic/{wsc_topic.pk}/')

    assert resp.status_code == 302
    assert MemorizationCard.objects.filter(user=learner).count() == 2


@pytest.mark.django_db
def test_adding_a_topic_twice_adds_nothing_further(client, learner, wsc_topic):
    client.force_login(learner)
    client.post(f'/accounts/memorize/add-topic/{wsc_topic.pk}/')
    client.post(f'/accounts/memorize/add-topic/{wsc_topic.pk}/')

    assert MemorizationCard.objects.filter(user=learner).count() == 2


@pytest.mark.django_db
def test_adding_a_topic_requires_login(client, wsc_topic):
    resp = client.post(f'/accounts/memorize/add-topic/{wsc_topic.pk}/')
    assert resp.status_code == 302
    assert '/accounts/login/' in resp['Location']


@pytest.mark.django_db
def test_confessions_do_not_offer_the_catechism_shortcuts(client, db):
    """WCF sections are prose, not question-and-answer; memorising them by
    section is a different exercise and the shortcut would mislead."""
    Catechism.objects.create(
        name='Westminster Confession', abbreviation='WCF', slug='wcf',
        total_questions=1, document_type=Catechism.CONFESSION,
        tradition=Catechism.WESTMINSTER,
    )
    body = client.get('/wcf/').content.decode()
    assert 'Memorise this catechism' not in body


@pytest.mark.django_db
def test_the_deck_page_is_in_the_sitemap(client, wsc_topic):
    body = client.get('/sitemap.xml').content.decode()
    assert '/accounts/memorize/' in body
