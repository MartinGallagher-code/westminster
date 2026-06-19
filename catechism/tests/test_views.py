import pytest
from django.contrib.auth.models import User
from django.test import Client

from catechism.models import Catechism, ComparisonSet
from .conftest import (
    TopicFactory, QuestionFactory,
    BibleBookFactory, ScriptureIndexFactory,
    ComparisonThemeFactory, ComparisonEntryFactory,
    ScripturePassageFactory, OntologyAttributeFactory, QuestionOntologyTagFactory,
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

    def test_home_has_social_metadata(self, client, setup_catechism):
        resp = client.get('/')
        content = resp.content.decode()
        assert '<link rel="canonical" href="http://testserver/">' in content
        assert 'property="og:image"' in content
        assert 'name="twitter:card" content="summary_large_image"' in content


@pytest.mark.django_db
class TestCatechismHomeView:
    def test_status_200(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert resp.status_code == 200

    def test_context(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert 'topics' in resp.context
        assert 'featured_question' in resp.context

    def test_grouped_context(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert 'grouped' in resp.context
        assert len(resp.context['grouped']) == 1
        assert len(resp.context['grouped'][0]['questions']) == 2

    def test_document_guide_context(self, client, setup_catechism):
        resp = client.get('/wsc/')
        assert resp.context['document_guide']['date'] == '1647'
        assert b'Historical Context' in resp.content

    def test_404_invalid_slug(self, client, setup_catechism):
        resp = client.get('/nonexistent/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestQuestionListRedirect:
    def test_redirects_to_home(self, client, setup_catechism):
        resp = client.get('/wsc/questions/')
        assert resp.status_code == 302
        assert resp.url == '/wsc/'


@pytest.mark.django_db
class TestLearnViews:
    def test_index_status_200(self, client, setup_catechism):
        resp = client.get('/learn/')
        assert resp.status_code == 200

    def test_index_lists_lesson(self, client, setup_catechism):
        resp = client.get('/learn/')
        assert resp.context['lesson_count'] >= 1
        assert b'The Chief End of Man' in resp.content

    def test_lesson_status_200(self, client, setup_catechism):
        resp = client.get('/learn/chief-end-of-man/')
        assert resp.status_code == 200

    def test_lesson_assembles_readings(self, client, setup_catechism):
        """The lesson pulls in the WSC chief-end question already in the DB."""
        resp = client.get('/learn/chief-end-of-man/')
        blocks = resp.context['reading_blocks']
        assert any(block['catechism'].slug == 'wsc' for block in blocks)
        assert b'glorify God' in resp.content

    def test_lesson_404_unknown_slug(self, client, setup_catechism):
        resp = client.get('/learn/nope/')
        assert resp.status_code == 404


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

    def test_renders_ontology_tags(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        attr = OntologyAttributeFactory(name='Necessity')
        QuestionOntologyTagFactory(question=q1, attribute=attr)

        resp = client.get('/wsc/questions/1/')

        assert resp.status_code == 200
        assert b'Ontology placement' in resp.content
        assert b'Necessity' in resp.content


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

    def test_search_has_query_metadata(self, client, setup_catechism):
        resp = client.get('/search/?q=chief+end')
        content = resp.content.decode()
        assert 'Search results for chief end' in content

    def test_search_matches_topic_name_from_generated_links(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        topic.name = 'Covenant Theology'
        topic.save()
        resp = client.get('/search/?q=Covenant+Theology')
        assert resp.status_code == 200
        assert q1 in resp.context['results']
        assert q2 in resp.context['results']


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
    def test_compare_index(self, client, setup_catechism):
        # A set is only shown when it has entries in an active-tradition catechism.
        cat, topic, q1, q2 = setup_catechism
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(name='Index Theme', slug='index-theme', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=2)
        resp = client.get('/compare/')
        assert resp.status_code == 200
        assert len(resp.context['comparison_sets']) == 1

    def test_compare_set(self, client, setup_catechism):
        # Themes are only shown when they have entries in an active-tradition catechism.
        cat, topic, q1, q2 = setup_catechism
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(name='God', slug='god', comparison_set=cs)
        ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=2)
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
class TestDoctrineViews:
    def test_doctrine_index_lists_active_themes(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(
            name='The Being of God',
            slug='being-of-god',
            locus='Theology Proper',
            comparison_set=cs,
        )
        ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=2)

        resp = client.get('/doctrine/')

        assert resp.status_code == 200
        assert resp.context['theme_count'] == 1
        assert b'The Being of God' in resp.content

    def test_doctrine_detail_links_comparison_theme(self, client, setup_catechism):
        cat, topic, q1, q2 = setup_catechism
        cs = ComparisonSet.objects.get(slug='westminster')
        theme = ComparisonThemeFactory(
            name='Creation',
            slug='creation',
            locus='Creation',
            comparison_set=cs,
        )
        ComparisonEntryFactory(theme=theme, catechism=cat, question_start=1, question_end=2)

        resp = client.get('/doctrine/creation/')

        assert resp.status_code == 200
        assert resp.context['theme_name'] == 'Creation'
        assert b'/compare/westminster/creation/' in resp.content

    def test_doctrine_detail_404_for_missing_theme(self, client, setup_catechism):
        resp = client.get('/doctrine/not-a-theme/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestSeoRoutes:
    def test_robots_references_sitemap(self, client):
        resp = client.get('/robots.txt')
        assert resp.status_code == 200
        assert resp['Content-Type'].startswith('text/plain')
        assert b'Allow: /' in resp.content
        assert b'Sitemap: http://testserver/sitemap.xml' in resp.content

    def test_sitemap_includes_core_routes(self, client, setup_catechism):
        resp = client.get('/sitemap.xml')
        content = resp.content.decode()
        assert resp.status_code == 200
        assert resp['Content-Type'].startswith('application/xml')
        assert '<loc>http://testserver/</loc>' in content
        assert '<loc>http://testserver/doctrine/</loc>' in content
        assert '<loc>http://testserver/wsc/</loc>' in content


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
