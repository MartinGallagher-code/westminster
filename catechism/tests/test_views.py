import pytest
from django.contrib.auth.models import User
from django.test import Client

from catechism.models import Catechism, ComparisonSet
from .conftest import (
    TopicFactory, QuestionFactory,
    BibleBookFactory, ScriptureIndexFactory,
    ComparisonThemeFactory, ComparisonEntryFactory,
    ScripturePassageFactory,
)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def setup_catechism(db):
    """Use the WSC seeded by migration 0004, add a topic and two questions."""
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
        proof_texts='Romans 11:36',
    )
    q2 = QuestionFactory(
        catechism=cat, number=2, topic=topic,
        question_text='What rule hath God given?',
        answer_text='The Word of God.',
    )
    return cat, topic, q1, q2


@pytest.mark.django_db
class TestHomeView:
    def test_status_200(self, client, setup_catechism):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_template(self, client, setup_catechism):
        resp = client.get('/')
        assert 'catechism/home.html' in [t.name for t in resp.templates]

    def test_context(self, client, setup_catechism):
        resp = client.get('/')
        assert 'catechisms' in resp.context
        assert 'featured' in resp.context


@pytest.mark.django_db
class TestCatechismHomeView:
    def test_status_200(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert resp.status_code == 200

    def test_context(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert 'topics' in resp.context
        assert 'featured_question' in resp.context

    def test_404_invalid_slug(self, client, setup_catechism):
        resp = client.get('/nonexistent/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestQuestionListView:
    def test_status_200(self, client, setup_catechism):
        resp = client.get('/wsc/questions/')
        assert resp.status_code == 200

    def test_grouped_context(self, client, setup_catechism):
        resp = client.get('/wsc/questions/')
        assert 'grouped' in resp.context
        assert len(resp.context['grouped']) == 1
        assert len(resp.context['grouped'][0]['questions']) == 2


@pytest.mark.django_db
class TestQuestionDetailView:
    def test_status_200(self, client, setup_catechism):
        resp = client.get('/wsc/questions/1/')
        assert resp.status_code == 200

    def test_context(self, client, setup_catechism):
        resp = client.get('/wsc/questions/1/')
        assert resp.context['question'].number == 1
        assert resp.context['next_question'].number == 2
        assert resp.context['previous_question'] is None

    def test_scripture_map(self, client, setup_catechism):
        ScripturePassageFactory(reference='Romans 11:36', text='For of him are all things.')
        resp = client.get('/wsc/questions/1/')
        assert 'Romans 11:36' in resp.context['scripture_map']

    def test_authenticated_user_sees_note_form(self, client, setup_catechism):
        User.objects.create_user('testuser', password='testpass123')
        client.login(username='testuser', password='testpass123')
        resp = client.get('/wsc/questions/1/')
        assert 'note_form' in resp.context

    def test_anonymous_no_note_form(self, client, setup_catechism):
        resp = client.get('/wsc/questions/1/')
        assert 'note_form' not in resp.context

    def test_404_invalid_number(self, client, setup_catechism):
        resp = client.get('/wsc/questions/999/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSearchView:
    def test_no_query(self, client, setup_catechism):
        resp = client.get('/search/')
        assert resp.status_code == 200
        assert len(resp.context['results']) == 0

    def test_with_query(self, client, setup_catechism):
        resp = client.get('/search/?q=chief+end')
        assert resp.status_code == 200
        assert len(resp.context['results']) == 1

    def test_filter_catechism(self, client, setup_catechism):
        resp = client.get('/search/?q=God&catechism=wsc')
        assert resp.status_code == 200
        results = resp.context['results']
        for r in results:
            assert r.catechism.slug == 'wsc'


@pytest.mark.django_db
class TestScriptureIndexView:
    def test_status_200(self, client):
        resp = client.get('/scripture/')
        assert resp.status_code == 200

    def test_context(self, client, db):
        BibleBookFactory(name='Genesis', slug='genesis', abbreviation='Gen', book_number=1, testament='OT')
        BibleBookFactory(name='Matthew', slug='matthew', abbreviation='Mat', book_number=40, testament='NT')
        resp = client.get('/scripture/')
        assert len(resp.context['ot_books']) == 1
        assert len(resp.context['nt_books']) == 1


@pytest.mark.django_db
class TestScriptureBookView:
    def test_status_200(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        book = BibleBookFactory(name='Romans', slug='romans', abbreviation='Rom', book_number=45, testament='NT')
        ScriptureIndexFactory(question=q1, book=book, reference='Romans 11:36')
        resp = client.get('/scripture/romans/')
        assert resp.status_code == 200
        assert resp.context['total_citations'] == 1


@pytest.mark.django_db
class TestCompareViews:
    def test_compare_index(self, client, db):
        resp = client.get('/compare/')
        assert resp.status_code == 200
        assert len(resp.context['comparison_sets']) == 1  # seeded by migration

    def test_compare_set(self, client, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        ComparisonThemeFactory(name='God', slug='god', comparison_set=cs)
        resp = client.get('/compare/westminster/')
        assert resp.status_code == 200
        assert len(resp.context['themes']) == 1

    def test_compare_theme(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(name='God', slug='god', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=2)
        resp = client.get('/compare/westminster/god/')
        assert resp.status_code == 200
        assert len(resp.context['columns']) == 1

    def test_legacy_theme_slug_redirects(self, client, db):
        cs = ComparisonSet.objects.get(slug='westminster')
        ComparisonThemeFactory(name='God', slug='god', comparison_set=cs)
        resp = client.get('/compare/god/')
        assert resp.status_code == 301
        assert '/compare/westminster/god/' in resp.url


@pytest.mark.django_db
class TestLegacyRedirects:
    def test_question_redirect(self, client, setup_catechism):
        resp = client.get('/questions/1/')
        assert resp.status_code == 301
        assert '/wsc/questions/1/' in resp.url

    def test_topic_redirect(self, client, setup_catechism):
        resp = client.get('/topics/of-god/')
        assert resp.status_code == 301
        assert '/wsc/topics/of-god/' in resp.url
