import factory
import pytest
from django.contrib.auth.models import User
from django.test import Client

from accounts.models import UserNote, Highlight
from catechism.models import Catechism
from catechism.tests.conftest import (
    TopicFactory, QuestionFactory,
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
