import pytest

from .conftest import (
    TopicFactory, QuestionFactory,
    FisherSubQuestionFactory,
)


@pytest.mark.django_db
class TestCatechism:
    def test_str(self, catechism):
        assert str(catechism) == 'WSC'

    def test_get_absolute_url(self, catechism):
        assert catechism.get_absolute_url() == '/wsc/'

    def test_is_confession_false(self, catechism):
        assert catechism.is_confession is False

    def test_is_confession_true(self, confession):
        assert confession.is_confession is True

    def test_item_name(self, catechism, confession):
        assert catechism.item_name == 'Question'
        assert confession.item_name == 'Section'

    def test_item_prefix(self, catechism, confession):
        assert catechism.item_prefix == 'Q'
        assert confession.item_prefix == ''

    def test_topic_name(self, catechism, confession):
        assert catechism.topic_name == 'Topic'
        assert confession.topic_name == 'Chapter'

    def test_get_item_list_url(self, catechism, confession):
        assert catechism.get_item_list_url() == '/wsc/'
        assert confession.get_item_list_url() == '/wcf/'


@pytest.mark.django_db
class TestQuestion:
    def test_str(self, question):
        assert str(question) == 'Q1: What is the chief end of man?'

    def test_display_number_catechism(self, question):
        assert question.display_number == '1'

    def test_display_number_confession(self, confession):
        topic = TopicFactory(catechism=confession, order=2, question_start=4, question_end=6)
        q = QuestionFactory(catechism=confession, number=5, topic=topic)
        assert q.display_number == '2.2'

    def test_get_absolute_url(self, question):
        assert question.get_absolute_url() == '/wsc/questions/1/'

    def test_get_previous_first(self, question):
        assert question.get_previous() is None

    def test_get_previous(self, question, question2):
        prev = question2.get_previous()
        assert prev is not None
        assert prev.number == 1

    def test_get_next(self, question, question2):
        nxt = question.get_next()
        assert nxt is not None
        assert nxt.number == 2

    def test_get_next_last(self, catechism, topic):
        q = QuestionFactory(catechism=catechism, number=10, topic=topic)
        assert q.get_next() is None

    def test_get_proof_text_list(self, question):
        refs = question.get_proof_text_list()
        assert refs == ['1 Corinthians 10:31', 'Romans 11:36']

    def test_get_proof_text_list_empty(self, question2):
        assert question2.get_proof_text_list() == []


@pytest.mark.django_db
class TestTopic:
    def test_str(self, topic):
        assert str(topic) == 'Of God'

    def test_display_start_catechism(self, topic):
        assert topic.display_start == '1'

    def test_display_start_confession(self, confession):
        t = TopicFactory(catechism=confession, order=3, question_start=5, question_end=8)
        assert t.display_start == '3.1'
        assert t.display_end == '3.4'

    def test_get_absolute_url(self, topic):
        url = topic.get_absolute_url()
        assert '/wsc/topics/of-god/' == url


@pytest.mark.django_db
class TestCommentary:
    def test_str(self, commentary):
        assert str(commentary) == "Fisher's Catechism on Q1"

    def test_fisher_subquestion_str(self, commentary):
        sq = FisherSubQuestionFactory(commentary=commentary, number=1)
        assert str(sq) == 'Q1.1'
