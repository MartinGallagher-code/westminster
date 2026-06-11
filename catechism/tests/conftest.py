import factory
import pytest
from django.contrib.auth.models import User

from catechism.models import (
    Catechism, Topic, Question, CommentarySource, Commentary,
    FisherSubQuestion, ScripturePassage, BibleBook, ScriptureIndex,
    ComparisonSet, ComparisonTheme, ComparisonEntry,
    OntologyLocus, OntologyAttribute, QuestionOntologyTag,
)


class CatechismFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Catechism

    name = 'Test Catechism'
    abbreviation = factory.Sequence(lambda n: f'TST{n}')
    slug = factory.Sequence(lambda n: f'tst{n}')
    description = 'Test catechism'
    total_questions = 10
    document_type = Catechism.CATECHISM


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic

    catechism = factory.SubFactory(CatechismFactory)
    name = factory.Sequence(lambda n: f'Topic {n}')
    slug = factory.Sequence(lambda n: f'topic-{n}')
    order = factory.Sequence(lambda n: n + 1)
    question_start = 1
    question_end = 5


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    catechism = factory.SubFactory(CatechismFactory)
    number = factory.Sequence(lambda n: n + 1)
    question_text = factory.Sequence(lambda n: f'What is question {n}?')
    answer_text = factory.Sequence(lambda n: f'Answer to question {n}.')
    topic = factory.SubFactory(TopicFactory, catechism=factory.SelfAttribute('..catechism'))
    proof_texts = ''


class CommentarySourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentarySource

    name = factory.Sequence(lambda n: f'Source {n}')
    slug = factory.Sequence(lambda n: f'source-{n}')
    author = factory.Sequence(lambda n: f'Author {n}')


class CommentaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commentary

    question = factory.SubFactory(QuestionFactory)
    source = factory.SubFactory(CommentarySourceFactory)
    body = 'Test commentary body text.'


class FisherSubQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FisherSubQuestion

    commentary = factory.SubFactory(CommentaryFactory)
    number = factory.Sequence(lambda n: n + 1)
    question_text = 'What is the sub-question?'
    answer_text = 'The sub-answer.'


class ScripturePassageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScripturePassage

    reference = factory.Sequence(lambda n: f'Genesis {n}:1')
    text = 'In the beginning God created the heaven and the earth.'


class BibleBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BibleBook

    name = factory.Sequence(lambda n: f'Book {n}')
    slug = factory.Sequence(lambda n: f'book-{n}')
    abbreviation = factory.Sequence(lambda n: f'Bk{n}')
    book_number = factory.Sequence(lambda n: n + 1)
    testament = 'OT'


class ScriptureIndexFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScriptureIndex

    question = factory.SubFactory(QuestionFactory)
    book = factory.SubFactory(BibleBookFactory)
    reference = factory.Sequence(lambda n: f'Genesis {n}:1')


class ComparisonSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComparisonSet

    name = factory.Sequence(lambda n: f'Set {n}')
    slug = factory.Sequence(lambda n: f'set-{n}')
    order = factory.Sequence(lambda n: n)


class ComparisonThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComparisonTheme

    comparison_set = factory.SubFactory(ComparisonSetFactory)
    name = factory.Sequence(lambda n: f'Theme {n}')
    slug = factory.Sequence(lambda n: f'theme-{n}')
    description = 'Test theme'
    order = factory.Sequence(lambda n: n)


class ComparisonEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComparisonEntry

    theme = factory.SubFactory(ComparisonThemeFactory)
    catechism = factory.SubFactory(CatechismFactory)
    question_start = 1
    question_end = 3


class OntologyLocusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OntologyLocus

    name = factory.Sequence(lambda n: f'Locus {n}')
    slug = factory.Sequence(lambda n: f'locus-{n}')
    icon = '*'
    color = '#6B2737'
    order = factory.Sequence(lambda n: n)
    atlas_path = factory.Sequence(lambda n: f'/westminster_standards/dimension/locus-{n}/')


class OntologyAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OntologyAttribute

    locus = factory.SubFactory(OntologyLocusFactory)
    name = factory.Sequence(lambda n: f'Attribute {n}')
    slug = factory.Sequence(lambda n: f'attribute-{n}')
    baseline_label = 'Baseline'
    baseline_slug = 'baseline'
    baseline_description = 'Baseline description.'
    order = factory.Sequence(lambda n: n)
    atlas_path = factory.Sequence(
        lambda n: f'/westminster_standards/dimension/locus/attribute-{n}/baseline/'
    )


class QuestionOntologyTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestionOntologyTag

    question = factory.SubFactory(QuestionFactory)
    attribute = factory.SubFactory(OntologyAttributeFactory)


@pytest.fixture
def catechism(db):
    """Get the WSC catechism seeded by migration 0004, adjusting total_questions for tests."""
    wsc = Catechism.objects.get(slug='wsc')
    wsc.total_questions = 10
    wsc.save()
    return wsc


@pytest.fixture
def confession(db):
    return CatechismFactory(
        name='Westminster Confession of Faith',
        abbreviation='WCF',
        slug='wcf',
        total_questions=5,
        document_type=Catechism.CONFESSION,
    )


@pytest.fixture
def topic(catechism):
    return TopicFactory(
        catechism=catechism,
        name='Of God',
        slug='of-god',
        order=1,
        question_start=1,
        question_end=3,
    )


@pytest.fixture
def question(catechism, topic):
    return QuestionFactory(
        catechism=catechism,
        number=1,
        question_text="What is the chief end of man?",
        answer_text="Man's chief end is to glorify God, and to enjoy him forever.",
        topic=topic,
        proof_texts='1 Corinthians 10:31; Romans 11:36',
    )


@pytest.fixture
def question2(catechism, topic):
    return QuestionFactory(
        catechism=catechism,
        number=2,
        question_text="What rule hath God given to direct us?",
        answer_text="The Word of God is the only rule.",
        topic=topic,
    )


@pytest.fixture
def commentary_source(db):
    return CommentarySourceFactory(
        name="Fisher's Catechism",
        slug='fisher-erskine',
        author='James Fisher',
    )


@pytest.fixture
def commentary(question, commentary_source):
    return CommentaryFactory(
        question=question,
        source=commentary_source,
        body='This is a test commentary on the chief end of man.',
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser', email='test@example.com', password='testpass123'
    )
