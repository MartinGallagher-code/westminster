import factory
import pytest
from django.contrib.auth.models import User
from django.test import Client

from accounts.models import UserNote, Highlight
from catechism.models import Catechism
from catechism.tests.conftest import (
    CatechismFactory, TopicFactory, QuestionFactory,
    CommentarySourceFactory, CommentaryFactory,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class UserNoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserNote

    user = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QuestionFactory)
    text = 'A test note.'


class HighlightFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Highlight

    user = factory.SubFactory(UserFactory)
    commentary = factory.SubFactory(CommentaryFactory)
    selected_text = 'highlighted text'
    occurrence_index = 0


@pytest.fixture
def user(db):
    return UserFactory(username='testuser')


@pytest.fixture
def other_user(db):
    return UserFactory(username='otheruser')


@pytest.fixture
def authenticated_client(user):
    c = Client()
    c.login(username='testuser', password='testpass123')
    return c


@pytest.fixture
def setup_data(db):
    """Use the WSC catechism seeded by migration 0004, then add topic/question/commentary."""
    cat = Catechism.objects.get(slug='wsc')
    cat.total_questions = 2
    cat.save()
    topic = TopicFactory(
        catechism=cat, name='Of God', slug='of-god',
        order=1, question_start=1, question_end=2,
    )
    q1 = QuestionFactory(
        catechism=cat, number=1, topic=topic,
        question_text='What is the chief end of man?',
        answer_text="Man's chief end is to glorify God.",
    )
    source = CommentarySourceFactory(
        name="Fisher's Catechism", slug='fisher-erskine', author='James Fisher',
    )
    commentary = CommentaryFactory(question=q1, source=source, body='Commentary body text.')
    return cat, topic, q1, source, commentary


@pytest.fixture
def heidelberg_setup(db):
    """Create a Heidelberg Catechism (non-Westminster catechism) with a topic and question."""
    cat = CatechismFactory(
        name='Heidelberg Catechism',
        abbreviation='HC',
        slug='hc',
        total_questions=129,
        document_type=Catechism.CATECHISM,
    )
    topic = TopicFactory(
        catechism=cat, name="Of Man's Misery", slug='of-mans-misery',
        order=1, question_start=1, question_end=2,
    )
    q = QuestionFactory(
        catechism=cat, number=1, topic=topic,
        question_text='What is your only comfort in life and death?',
        answer_text='That I am not my own, but belong to my faithful Savior Jesus Christ.',
    )
    return cat, topic, q


@pytest.fixture
def belgic_setup(db):
    """Create a Belgic Confession (non-Westminster confession) with a topic and question."""
    cat = CatechismFactory(
        name='Belgic Confession',
        abbreviation='BC',
        slug='bc',
        total_questions=37,
        document_type=Catechism.CONFESSION,
    )
    topic = TopicFactory(
        catechism=cat, name='The Only God', slug='the-only-god',
        order=1, question_start=1, question_end=1,
    )
    q = QuestionFactory(
        catechism=cat, number=1, topic=topic,
        question_text='The Only God',
        answer_text='We all believe with the heart and confess with the mouth...',
    )
    return cat, topic, q
