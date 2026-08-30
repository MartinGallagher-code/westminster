import pytest
from django.contrib.auth.models import User
from django.test import Client

from catechism.models import Catechism, ComparisonSet
from catechism.views import GROUPED_SEARCH_SAMPLE, SEARCH_PAGE_SIZE
from .conftest import (
    CatechismFactory, TopicFactory, QuestionFactory,
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

    def test_lesson_teaches_with_prose(self, client, setup_catechism):
        """The lesson renders teaching prose, not a re-render of the Q&A."""
        resp = client.get('/learn/chief-end-of-man/')
        assert resp.context['sections']
        assert b'chief, or' in resp.content  # teaching prose, authored in the guide

    def test_lesson_links_to_texts(self, client, setup_catechism):
        """References resolve to links into the underlying question pages."""
        resp = client.get('/learn/chief-end-of-man/')
        groups = resp.context['text_groups']
        assert any(g['abbreviation'] == 'WSC' for g in groups)
        assert b'/wsc/questions/1/' in resp.content

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

    # ── Result volume ────────────────────────────────────────────────────
    #
    # Every match used to render on one page: "the" returned 633KB of HTML.
    # Across documents each group now shows a sample and offers the rest
    # behind its own filter; within one document the list pages.

    def test_group_samples_and_offers_the_rest(self, client, setup_catechism):
        cat, topic, _, _ = setup_catechism
        for number in range(3, 3 + GROUPED_SEARCH_SAMPLE + 5):
            QuestionFactory(
                catechism=cat, number=number, topic=topic,
                question_text='What is God?', answer_text='God is a Spirit.',
            )

        resp = client.get('/search/?q=God')
        group = resp.context['grouped_results'][0]

        assert len(group['questions']) == GROUPED_SEARCH_SAMPLE
        assert group['total'] > GROUPED_SEARCH_SAMPLE
        assert group['has_more'] is True
        assert f'catechism={cat.slug}' in group['more_url']
        # The count shown is the true one, not the size of the sample.
        assert resp.context['total_results'] == group['total']

    def test_small_group_is_not_truncated(self, client, setup_catechism):
        resp = client.get('/search/?q=chief+end')
        group = resp.context['grouped_results'][0]
        assert group['has_more'] is False
        assert len(group['questions']) == group['total']

    def test_unfiltered_search_is_not_paginated(self, client, setup_catechism):
        resp = client.get('/search/?q=God')
        assert resp.context['paginator'] is None

    def test_filtered_search_pages_the_whole_document(self, client, setup_catechism):
        cat, topic, _, _ = setup_catechism
        for number in range(3, 3 + SEARCH_PAGE_SIZE + 5):
            QuestionFactory(
                catechism=cat, number=number, topic=topic,
                question_text='What is God?', answer_text='God is a Spirit.',
            )

        resp = client.get(f'/search/?q=God&catechism={cat.slug}')
        assert resp.context['paginator'].num_pages == 2
        assert len(resp.context['results']) == SEARCH_PAGE_SIZE
        # A page of one document shows everything on it — nothing held back.
        assert resp.context['grouped_results'][0]['has_more'] is False
        assert len(resp.context['grouped_results'][0]['questions']) == SEARCH_PAGE_SIZE

        total = resp.context['paginator'].count
        page_two = client.get(f'/search/?q=God&catechism={cat.slug}&page=2')
        assert page_two.status_code == 200
        assert len(page_two.context['results']) == total - SEARCH_PAGE_SIZE
        # The reported total is the whole result set, not this page.
        assert page_two.context['total_results'] == total

    def test_paging_links_keep_the_query_and_filter(self, client, setup_catechism):
        cat, topic, _, _ = setup_catechism
        for number in range(3, 3 + SEARCH_PAGE_SIZE + 5):
            QuestionFactory(
                catechism=cat, number=number, topic=topic,
                question_text='What is God?', answer_text='God is a Spirit.',
            )

        body = client.get(f'/search/?q=God&catechism={cat.slug}').content.decode()
        assert f'?q=God&amp;catechism={cat.slug}&amp;page=2' in body

    def test_atlas_matches_are_not_repeated_on_every_page(self, client, setup_catechism):
        cat, topic, _, _ = setup_catechism
        for number in range(3, 3 + SEARCH_PAGE_SIZE + 5):
            QuestionFactory(
                catechism=cat, number=number, topic=topic,
                question_text='What is God?', answer_text='God is a Spirit.',
            )

        first = client.get(f'/search/?q=God&catechism={cat.slug}')
        second = client.get(f'/search/?q=God&catechism={cat.slug}&page=2')
        assert first.context['show_atlas_results'] is True
        assert second.context['show_atlas_results'] is False


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


@pytest.mark.django_db
class TestCompareIndexPresets:
    def _seed_westminster(self):
        wsc = Catechism.objects.get(slug='wsc')
        wsc.tradition = Catechism.WESTMINSTER
        wsc.save()
        wcf = CatechismFactory(
            slug='wcf', abbreviation='WCF', tradition=Catechism.WESTMINSTER,
            document_type=Catechism.CONFESSION,
        )
        wlc = CatechismFactory(
            slug='wlc', abbreviation='WLC', tradition=Catechism.WESTMINSTER,
        )
        for cat in (wsc, wcf, wlc):
            ComparisonEntryFactory(catechism=cat)
        return wsc, wcf, wlc

    def test_westminster_preset_present(self, client):
        self._seed_westminster()
        resp = client.get('/compare/')
        assert resp.status_code == 200
        presets = resp.context['comparison_presets']
        by_name = {p['name']: p for p in presets}
        assert 'Westminster Standards' in by_name
        assert set(by_name['Westminster Standards']['slugs']) == {'wcf', 'wlc', 'wsc'}
        assert by_name['Westminster Standards']['docs_param']

    def test_preset_rendered_in_template(self, client):
        self._seed_westminster()
        resp = client.get('/compare/')
        content = resp.content.decode()
        assert 'preset-btn' in content
        assert 'Westminster Standards' in content

    def test_preset_dropped_when_only_one_doc_available(self, client):
        """A preset needs >= 2 available documents or it is omitted."""
        wsc = Catechism.objects.get(slug='wsc')
        wsc.tradition = Catechism.WESTMINSTER
        wsc.save()
        ComparisonEntryFactory(catechism=wsc)
        resp = client.get('/compare/')
        names = [p['name'] for p in resp.context['comparison_presets']]
        assert 'Westminster Standards' not in names


@pytest.mark.django_db
class TestAboutView:
    """Every other page assumes the vocabulary; this one supplies it."""

    def test_renders(self, client, setup_catechism):
        resp = client.get('/about/')
        assert resp.status_code == 200
        assert b'What are the Reformed standards?' in resp.content

    def test_counts_the_corpus_rather_than_hardcoding_it(self, client, setup_catechism):
        cat, topic, _, _ = setup_catechism
        resp = client.get('/about/')

        assert resp.context['document_count'] == Catechism.objects.filter(
            tradition__in=('westminster',),
        ).count()
        assert resp.context['item_count'] == 2
        loaded = [
            document
            for collection in resp.context['collections']
            for document in collection['documents']
        ]
        assert cat in loaded

    def test_lists_only_documents_in_active_collections(self, client, setup_catechism):
        """A document behind an unselected collection is not advertised here."""
        dormant = CatechismFactory(
            slug='belgic-test', abbreviation='BCt', tradition='three_forms_of_unity',
        )
        QuestionFactory(catechism=dormant)

        resp = client.get('/about/')
        listed = [
            document
            for collection in resp.context['collections']
            for document in collection['documents']
        ]
        assert dormant not in listed

    def test_is_reachable_from_the_footer(self, client, setup_catechism):
        body = client.get('/').content.decode()
        assert 'href="/about/"' in body

    def test_is_in_the_sitemap(self, client, setup_catechism):
        assert b'/about/' in client.get('/sitemap.xml').content
