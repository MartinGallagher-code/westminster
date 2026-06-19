from collections import defaultdict
from datetime import date
import re
from xml.sax.saxutils import escape

from django.db import connection
from django.db.models import Q, Count, Prefetch
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .atlas import atlas_url, atlas_work_url
from .document_guides import get_document_guide
from .teaching_guide import (
    get_guide_intro, get_lessons, get_lesson, get_adjacent_lessons,
)
from .models import (
    Catechism, Topic, Question, Commentary, FisherSubQuestion,
    ScripturePassage, StandardCrossReference,
    BibleBook, ScriptureIndex, ComparisonSet, ComparisonTheme,
    ComparisonEntry, QuestionDoctrineHead, QuestionOntologyTag,
)
from .utils import VALID_TRADITIONS, get_active_traditions


SEARCH_STOP_WORDS = {
    'a', 'an', 'and', 'by', 'for', 'from', 'in', 'into', 'is', 'of', 'on',
    'or', 'the', 'to', 'with',
}


def _comparison_sets_for_traditions(active_traditions):
    qs = ComparisonSet.objects.filter(
        themes__entries__catechism__tradition__in=active_traditions
    ).distinct().order_by('order')
    return qs.exclude(themes__entries__catechism__tradition=Catechism.OTHER)


def _comparison_themes_for_traditions(active_traditions):
    return ComparisonTheme.objects.filter(
        entries__catechism__tradition__in=active_traditions
    ).exclude(
        entries__catechism__tradition=Catechism.OTHER
    ).annotate(
        active_entry_count=Count(
            'entries',
            filter=Q(entries__catechism__tradition__in=active_traditions),
            distinct=True,
        )
    ).select_related('comparison_set').distinct()


def _search_terms(query):
    return [
        term for term in re.findall(r"[A-Za-z0-9']+", query.lower())
        if len(term) > 2 and term not in SEARCH_STOP_WORDS
    ]


def _search_questions(query, active_traditions):
    base_qs = Question.objects.filter(
        catechism__tradition__in=active_traditions
    ).select_related('topic', 'catechism')
    terms = _search_terms(query)

    if connection.vendor == 'postgresql':
        from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

        vector = (
            SearchVector('question_text', weight='A') +
            SearchVector('answer_text', weight='B') +
            SearchVector('topic__name', weight='B') +
            SearchVector('proof_texts', weight='C')
        )
        search_query = SearchQuery(query, search_type='websearch')
        for term in terms:
            search_query |= SearchQuery(term, search_type='plain')
        return base_qs.annotate(
            search=vector,
            rank=SearchRank(vector, search_query),
        ).filter(search=search_query).order_by(
            '-rank', 'catechism__abbreviation', 'number'
        )

    search_filter = (
        Q(question_text__icontains=query) |
        Q(answer_text__icontains=query) |
        Q(topic__name__icontains=query) |
        Q(proof_texts__icontains=query)
    )
    for term in terms:
        search_filter |= (
            Q(question_text__icontains=term) |
            Q(answer_text__icontains=term) |
            Q(topic__name__icontains=term) |
            Q(proof_texts__icontains=term)
        )
    return base_qs.filter(search_filter).distinct().order_by('catechism__abbreviation', 'number')


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse('catechism:sitemap_xml'))
    body = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
    return HttpResponse(body, content_type='text/plain')


def sitemap_xml(request):
    urls = [
        reverse('catechism:home'),
        reverse('catechism:search'),
        reverse('catechism:scripture_index'),
        reverse('catechism:compare_index'),
        reverse('catechism:doctrine_index'),
        reverse('accounts:signup'),
        reverse('accounts:login'),
    ]

    supported_catechisms = Catechism.objects.filter(
        tradition__in=VALID_TRADITIONS
    ).prefetch_related('topics', 'questions').order_by('tradition', 'abbreviation')
    for catechism in supported_catechisms:
        urls.append(catechism.get_absolute_url())
        urls.extend(topic.get_absolute_url() for topic in catechism.topics.all())
        urls.extend(question.get_absolute_url() for question in catechism.questions.all())

    urls.extend(book.get_absolute_url() for book in BibleBook.objects.all())
    urls.extend(
        comparison_set.get_absolute_url()
        for comparison_set in _comparison_sets_for_traditions(VALID_TRADITIONS)
    )

    comparison_themes = _comparison_themes_for_traditions(VALID_TRADITIONS)
    urls.extend(theme.get_absolute_url() for theme in comparison_themes)
    urls.extend(
        reverse('catechism:doctrine_detail', kwargs={'theme_slug': slug})
        for slug in comparison_themes.values_list('slug', flat=True).distinct()
    )

    seen = set()
    locs = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        locs.append(request.build_absolute_uri(url))

    body = ['<?xml version="1.0" encoding="UTF-8"?>']
    body.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc in locs:
        body.append(f'  <url><loc>{escape(loc)}</loc></url>')
    body.append('</urlset>')
    return HttpResponse('\n'.join(body), content_type='application/xml')


class CatechismMixin:
    """Mixin that retrieves the catechism from the URL and adds it to context."""

    def dispatch(self, request, *args, **kwargs):
        self.catechism = get_object_or_404(Catechism, slug=kwargs['catechism_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['catechism'] = self.catechism
        return ctx


class HomeView(TemplateView):
    template_name = 'catechism/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        catechisms = list(Catechism.objects.filter(tradition__in=active_traditions))
        day_of_year = date.today().timetuple().tm_yday
        for cat in catechisms:
            cat.featured_question = Question.objects.filter(
                catechism=cat,
                number=(day_of_year % cat.total_questions) + 1
            ).select_related('topic').first()
        ctx['catechisms'] = catechisms
        if catechisms:
            hero_cat = catechisms[day_of_year % len(catechisms)]
            ctx['featured'] = hero_cat.featured_question
        else:
            ctx['featured'] = None
        ctx['primary_docs'] = [
            cat for slug in ['wsc', 'wcf', 'wlc']
            for cat in catechisms
            if cat.slug == slug
        ]
        ctx['comparison_sets'] = ComparisonSet.objects.filter(
            themes__entries__catechism__tradition__in=active_traditions
        ).distinct().order_by('order')[:3]
        ctx['suggested_searches'] = [
            'justification',
            'baptism',
            'Sabbath',
            'covenant of grace',
        ]
        ctx['atlas_home_url'] = atlas_url()
        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            ctx['recent_note'] = UserNote.objects.filter(
                user=self.request.user
            ).select_related(
                'question', 'question__catechism', 'question__topic'
            ).order_by('-updated_at').first()
        return ctx


class CatechismHomeView(CatechismMixin, TemplateView):
    template_name = 'catechism/catechism_home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['document_guide'] = get_document_guide(self.catechism.slug)
        topics = Topic.objects.filter(catechism=self.catechism)
        ctx['topics'] = topics

        questions = Question.objects.filter(
            catechism=self.catechism
        ).select_related('topic')
        ctx['question_count'] = questions.count()

        questions_by_topic = defaultdict(list)
        for q in questions:
            questions_by_topic[q.topic_id].append(q)
        ctx['grouped'] = [
            {'topic': topic, 'questions': questions_by_topic.get(topic.id, [])}
            for topic in topics
        ]

        day_of_year = date.today().timetuple().tm_yday
        ctx['featured_question'] = Question.objects.filter(
            catechism=self.catechism,
            number=(day_of_year % self.catechism.total_questions) + 1
        ).select_related('topic').first()
        return ctx


class DoctrineIndexView(TemplateView):
    template_name = 'catechism/doctrine_index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        themes = _comparison_themes_for_traditions(active_traditions).order_by(
            'locus', 'order', 'name'
        )
        grouped = defaultdict(list)
        for theme in themes:
            grouped[theme.locus or 'General Doctrine'].append(theme)
        ctx['locus_groups'] = [
            {'locus': locus, 'themes': items}
            for locus, items in grouped.items()
        ]
        ctx['theme_count'] = themes.count()
        return ctx


class DoctrineDetailView(TemplateView):
    template_name = 'catechism/doctrine_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        themes = _comparison_themes_for_traditions(active_traditions).filter(
            slug=self.kwargs['theme_slug']
        ).order_by('comparison_set__order', 'order')
        if not themes.exists():
            raise Http404
        ctx['themes'] = themes
        ctx['primary_theme'] = themes.first()
        ctx['theme_name'] = ctx['primary_theme'].name
        ctx['theme_description'] = ctx['primary_theme'].description
        return ctx


def _resolve_text_links(text_refs):
    """Resolve teaching-guide ``text`` references into link dicts for templates.

    Each reference names a catechism slug and question/section numbers; the
    result is a flat list of links (skipping any document not in the database).
    """
    links = []
    for ref in text_refs:
        catechism = Catechism.objects.filter(slug=ref['catechism']).first()
        if catechism is None:
            continue
        questions = Question.objects.filter(
            catechism=catechism, number__in=ref['numbers']
        ).select_related('catechism', 'topic').order_by('number')
        for question in questions:
            links.append({
                'pk': question.pk,
                'url': question.get_absolute_url(),
                'label': (
                    f"{catechism.abbreviation} {catechism.item_prefix}"
                    f"{question.display_number}"
                ),
                'abbreviation': catechism.abbreviation,
                'catechism_name': catechism.name,
                'question_text': question.question_text,
            })
    return links


class LearnIndexView(TemplateView):
    """Landing page for the guided teaching path."""
    template_name = 'catechism/learn_index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['intro'] = get_guide_intro()
        units = []
        units_by_name = {}
        for lesson in get_lessons():
            unit_name = lesson.get('unit', 'Lessons')
            if unit_name not in units_by_name:
                units_by_name[unit_name] = {'name': unit_name, 'lessons': []}
                units.append(units_by_name[unit_name])
            units_by_name[unit_name]['lessons'].append(lesson)
        for unit in units:
            unit['lessons'].sort(key=lambda lesson_data: lesson_data.get('order', 0))
        ctx['units'] = units
        ctx['lesson_count'] = len(get_lessons())
        return ctx


class LearnLessonView(TemplateView):
    """A single lesson: teaching prose that links out to the texts it expounds."""
    template_name = 'catechism/learn_lesson.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lesson = get_lesson(self.kwargs['lesson_slug'])
        if lesson is None:
            raise Http404
        ctx['lesson'] = lesson

        # Resolve each section's text references into links, and aggregate a
        # de-duplicated "texts in this lesson" list grouped by document.
        sections = []
        text_groups = []
        groups_by_abbr = {}
        seen_pks = set()
        for section in lesson.get('sections', []):
            links = _resolve_text_links(section.get('texts', []))
            sections.append({
                'heading': section.get('heading'),
                'body': section.get('body', []),
                'text_links': links,
            })
            for link in links:
                if link['pk'] in seen_pks:
                    continue
                seen_pks.add(link['pk'])
                abbr = link['abbreviation']
                if abbr not in groups_by_abbr:
                    groups_by_abbr[abbr] = {
                        'abbreviation': abbr,
                        'name': link['catechism_name'],
                        'links': [],
                    }
                    text_groups.append(groups_by_abbr[abbr])
                groups_by_abbr[abbr]['links'].append(link)
        ctx['sections'] = sections
        ctx['text_groups'] = text_groups

        theme_slug = lesson.get('comparison_theme')
        if theme_slug:
            active_traditions = get_active_traditions(self.request)
            ctx['comparison_theme'] = _comparison_themes_for_traditions(
                active_traditions
            ).filter(slug=theme_slug).first()

        previous_lesson, next_lesson = get_adjacent_lessons(lesson['slug'])
        ctx['previous_lesson'] = previous_lesson
        ctx['next_lesson'] = next_lesson
        return ctx


class QuestionDetailView(CatechismMixin, DetailView):
    template_name = 'catechism/question_detail.html'
    context_object_name = 'question'

    def get_object(self):
        return get_object_or_404(
            Question.objects.select_related('topic', 'catechism').prefetch_related(
                Prefetch(
                    'commentaries',
                    queryset=Commentary.objects.select_related('source').prefetch_related(
                        Prefetch(
                            'sub_questions',
                            queryset=FisherSubQuestion.objects.order_by('number')
                        )
                    )
                ),
                Prefetch(
                    'ontology_tags',
                    queryset=QuestionOntologyTag.objects.select_related(
                        'attribute', 'attribute__locus'
                    ),
                ),
                Prefetch(
                    'doctrine_head_links',
                    queryset=QuestionDoctrineHead.objects.select_related(
                        'doctrine_head', 'doctrine_head__locus'
                    ),
                ),
            ),
            catechism=self.catechism,
            number=self.kwargs['number']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.object
        ctx['previous_question'] = q.get_previous()
        ctx['next_question'] = q.get_next()
        ctx['ontology_tags'] = list(q.ontology_tags.all())
        ctx['doctrine_heads'] = [
            link.doctrine_head for link in q.doctrine_head_links.all()
        ]

        # Build sidebar document navigation grouped by topic
        topics = Topic.objects.filter(catechism=self.catechism)
        nav_questions = Question.objects.filter(
            catechism=self.catechism
        ).select_related('topic').order_by('number')
        nav_by_topic = defaultdict(list)
        for nav_q in nav_questions:
            nav_by_topic[nav_q.topic_id].append(nav_q)
        ctx['nav_grouped'] = [
            {'topic': topic, 'questions': nav_by_topic.get(topic.id, [])}
            for topic in topics
        ]

        # Build scripture text lookup for proof texts
        refs = q.get_proof_text_list()
        if refs:
            passages = ScripturePassage.objects.filter(reference__in=refs)
            ctx['scripture_map'] = {p.reference: p.text for p in passages}
            found_refs = set(ctx['scripture_map'].keys())
            for ref in refs:
                if ref not in found_refs:
                    passage = ScripturePassage.objects.filter(reference=ref).first()
                    if passage:
                        ctx['scripture_map'][ref] = passage.text
        else:
            ctx['scripture_map'] = {}

        active_traditions = get_active_traditions(self.request)

        # Generic cross-references (any catechism to any catechism), filtered to active traditions
        cross_ref_qs = StandardCrossReference.objects.filter(
            Q(source_question=q) | Q(target_question=q)
        ).select_related(
            'source_question__catechism',
            'source_question__topic',
            'target_question__catechism',
            'target_question__topic',
        )

        cross_ref_groups = defaultdict(list)
        for cr in cross_ref_qs:
            if cr.source_question_id == q.id:
                other = cr.target_question
            else:
                other = cr.source_question
            # Only show cross-refs to documents in active traditions
            if other.catechism.tradition in active_traditions:
                cross_ref_groups[other.catechism.abbreviation].append(other)

        # Sort each group by question number and cap display size
        MAX_CROSSREFS_PER_GROUP = 8
        for abbr in cross_ref_groups:
            cross_ref_groups[abbr].sort(key=lambda x: x.number)
            if len(cross_ref_groups[abbr]) > MAX_CROSSREFS_PER_GROUP:
                cross_ref_groups[abbr] = cross_ref_groups[abbr][:MAX_CROSSREFS_PER_GROUP]

        ctx['cross_ref_groups'] = dict(cross_ref_groups)

        # Comparison themes that include this question, with at least one active-tradition entry
        ctx['comparison_themes'] = ComparisonTheme.objects.filter(
            entries__catechism=q.catechism,
            entries__question_start__lte=q.number,
            entries__question_end__gte=q.number,
        ).filter(
            entries__catechism__tradition__in=active_traditions
        ).distinct()

        # Chapter mode: all questions in the same topic, with their scripture maps
        chapter_questions = list(
            Question.objects.filter(
                catechism=self.catechism, topic=q.topic
            ).select_related('topic').order_by('number')
        )
        ctx['chapter_questions'] = chapter_questions

        # Build scripture maps for all chapter questions (for chapter mode)
        chapter_scripture_map = {}
        for cq in chapter_questions:
            if cq.id == q.id:
                continue  # Already built above
            cq_refs = cq.get_proof_text_list()
            if cq_refs:
                for p in ScripturePassage.objects.filter(reference__in=cq_refs):
                    chapter_scripture_map[p.reference] = p.text
        ctx['chapter_scripture_map'] = {**chapter_scripture_map, **ctx['scripture_map']}

        ctx['atlas_url'] = atlas_work_url(self.catechism.slug, q)

        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            from accounts.forms import NoteForm
            ctx['user_note'] = UserNote.objects.filter(
                user=self.request.user, question=q
            ).first()
            ctx['note_form'] = NoteForm()

        return ctx


class TopicListRedirectView(CatechismMixin, View):
    """Redirect old topic/chapter list to the home page."""

    def get(self, request, *args, **kwargs):
        return redirect(self.catechism.get_absolute_url())


class TopicDetailView(CatechismMixin, DetailView):
    template_name = 'catechism/topic_detail.html'
    context_object_name = 'topic'

    def get_object(self):
        return get_object_or_404(
            Topic, catechism=self.catechism, slug=self.kwargs['slug']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['questions'] = Question.objects.filter(
            catechism=self.catechism, topic=self.object
        )
        return ctx


class SearchView(ListView):
    template_name = 'catechism/search_results.html'
    context_object_name = 'results'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Question.objects.none()

        active_traditions = get_active_traditions(self.request)
        qs = _search_questions(query, active_traditions)

        catechism_slug = self.request.GET.get('catechism', '')
        if catechism_slug:
            qs = qs.filter(catechism__slug=catechism_slug)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        active_traditions = get_active_traditions(self.request)
        ctx['selected_catechism_slug'] = self.request.GET.get('catechism', '')
        ctx['all_catechisms'] = Catechism.objects.filter(
            tradition__in=active_traditions
        ).order_by('abbreviation')
        ctx['suggested_searches'] = [
            'faith',
            'justification',
            'Scripture',
            'Lord\'s Supper',
            'church discipline',
        ]

        tradition_order = {'westminster': 0, 'three_forms_of_unity': 1, 'other': 2}
        document_order = {
            'wcf': 0,
            'wlc': 1,
            'wsc': 2,
            'heidelberg': 3,
            'belgic': 4,
            'dort': 5,
            'pca-bco': 8,
        }
        grouped = defaultdict(list)
        catechism_map = {}
        for q in ctx['results']:
            cat = q.catechism
            grouped[cat.pk].append(q)
            catechism_map[cat.pk] = cat

        ordered_cats = sorted(
            catechism_map.values(),
            key=lambda c: (
                tradition_order.get(c.tradition, 99),
                document_order.get(c.slug, 50),
                c.abbreviation,
            ),
        )
        ctx['grouped_results'] = [
            {'catechism': cat, 'questions': grouped[cat.pk]}
            for cat in ordered_cats
        ]
        ctx['total_results'] = sum(len(g['questions']) for g in ctx['grouped_results'])
        return ctx


class ScriptureIndexView(TemplateView):
    template_name = 'catechism/scripture_index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        books = BibleBook.objects.annotate(
            citation_count=Count(
                'index_entries',
                filter=Q(index_entries__question__catechism__tradition__in=active_traditions),
            )
        ).order_by('book_number')
        ctx['ot_books'] = [b for b in books if b.testament == 'OT']
        ctx['nt_books'] = [b for b in books if b.testament == 'NT']
        return ctx


class ScriptureBookView(DetailView):
    template_name = 'catechism/scripture_book.html'
    model = BibleBook
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        entries = ScriptureIndex.objects.filter(
            book=self.object,
            question__catechism__tradition__in=active_traditions,
        ).select_related('question__catechism', 'question__topic').order_by(
            'question__catechism__abbreviation', 'question__number', 'reference',
        )

        grouped = defaultdict(list)
        catechism_map = {}
        for entry in entries:
            cat = entry.question.catechism
            grouped[cat.pk].append({'question': entry.question, 'reference': entry.reference})
            catechism_map[cat.pk] = cat

        tradition_order = {'westminster': 0, 'three_forms_of_unity': 1, 'other': 2}
        ordered_cats = sorted(
            catechism_map.values(),
            key=lambda c: (tradition_order.get(c.tradition, 99), c.abbreviation),
        )
        ctx['grouped_entries'] = [
            {'catechism': cat, 'entries': grouped[cat.pk]}
            for cat in ordered_cats
        ]
        ctx['total_citations'] = len(entries)
        return ctx


class CompareIndexView(ListView):
    template_name = 'catechism/compare_index.html'
    model = ComparisonSet
    context_object_name = 'comparison_sets'

    def get_queryset(self):
        # Only show sets where ALL catechisms in the set belong to active traditions.
        # First include sets that have at least one active-tradition entry,
        # then exclude any that also have entries from non-active traditions
        # (including tradition='other').
        active_traditions = set(get_active_traditions(self.request))
        qs = ComparisonSet.objects.filter(
            themes__entries__catechism__tradition__in=active_traditions
        ).distinct().order_by('order')
        inactive_traditions = set(
            Catechism.objects.exclude(
                tradition__in=active_traditions
            ).values_list('tradition', flat=True).distinct()
        )
        if inactive_traditions:
            qs = qs.exclude(
                themes__entries__catechism__tradition__in=inactive_traditions
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        ctx['all_catechisms'] = Catechism.objects.filter(
            tradition__in=active_traditions,
            comparison_entries__isnull=False,
        ).distinct()
        ctx['active_traditions'] = active_traditions
        return ctx


def _build_columns(entries):
    """Build column data from ComparisonEntry queryset."""
    columns = []
    for entry in entries:
        questions = entry.get_questions()
        first_q = questions.first()
        last_q = questions.last()
        columns.append({
            'catechism': entry.catechism,
            'question_start': entry.question_start,
            'question_end': entry.question_end,
            'display_start': first_q.display_number if first_q else str(entry.question_start),
            'display_end': last_q.display_number if last_q else str(entry.question_end),
            'questions': questions,
        })
    return columns


class CustomCompareView(TemplateView):
    template_name = 'catechism/compare_custom.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active_traditions = get_active_traditions(self.request)

        # Parse document slugs from query parameter
        docs_param = self.request.GET.get('docs', '')
        selected_slugs = [s.strip() for s in docs_param.split(',') if s.strip()]

        # Validate against active-tradition catechisms only
        all_catechisms = Catechism.objects.filter(
            tradition__in=active_traditions,
            comparison_entries__isnull=False,
        ).distinct()
        valid_slugs = set(all_catechisms.values_list('slug', flat=True))
        selected_slugs = [s for s in selected_slugs if s in valid_slugs]

        ctx['all_catechisms'] = all_catechisms
        ctx['selected_slugs'] = selected_slugs
        ctx['selected_catechisms'] = Catechism.objects.filter(slug__in=selected_slugs)

        if len(selected_slugs) < 2:
            ctx['themes'] = []
            ctx['error'] = 'Select at least two documents to compare.'
            return ctx

        # Find all themes that have entries for at least one of the selected docs
        themes_with_matches = ComparisonTheme.objects.filter(
            entries__catechism__slug__in=selected_slugs
        ).distinct().select_related('comparison_set').prefetch_related(
            Prefetch(
                'entries',
                queryset=ComparisonEntry.objects.filter(
                    catechism__slug__in=selected_slugs
                ).select_related('catechism'),
                to_attr='matching_entries'
            )
        )

        # Group by theme slug and merge across sets
        slug_groups = defaultdict(list)
        for theme in themes_with_matches:
            slug_groups[theme.slug].append(theme)

        # Keep themes where at least 2 selected documents are covered
        result_themes = []
        for slug, theme_list in slug_groups.items():
            matched_cats = set()
            for theme in theme_list:
                for entry in theme.matching_entries:
                    matched_cats.add(entry.catechism.slug)
            if len(matched_cats) >= 2:
                result_themes.append({
                    'theme': theme_list[0],
                    'locus': theme_list[0].locus,
                })

        result_themes.sort(key=lambda x: (x['locus'], x['theme'].order))

        ctx['themes'] = result_themes
        ctx['docs_param'] = ','.join(selected_slugs)
        return ctx


class CustomCompareThemeView(TemplateView):
    template_name = 'catechism/compare_custom_theme.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active_traditions = get_active_traditions(self.request)
        docs_param = self.request.GET.get('docs', '')
        selected_slugs = [s.strip() for s in docs_param.split(',') if s.strip()]
        theme_slug = self.kwargs['theme_slug']

        # Find all themes with this slug across all sets
        themes = ComparisonTheme.objects.filter(slug=theme_slug)
        if not themes.exists():
            raise Http404

        primary_theme = themes.first()
        ctx['theme'] = primary_theme

        # Collect entries filtered to selected docs AND active traditions
        all_entries = ComparisonEntry.objects.filter(
            theme__slug=theme_slug,
            catechism__slug__in=selected_slugs,
            catechism__tradition__in=active_traditions,
        ).select_related('catechism')

        # Deduplicate by catechism (prefer first occurrence)
        seen = set()
        unique_entries = []
        for entry in all_entries:
            if entry.catechism.slug not in seen:
                seen.add(entry.catechism.slug)
                unique_entries.append(entry)

        columns = _build_columns(unique_entries)

        # Sort columns to match the order in selected_slugs
        slug_order = {s: i for i, s in enumerate(selected_slugs)}
        columns.sort(key=lambda c: slug_order.get(c['catechism'].slug, 999))

        ctx['columns'] = columns
        ctx['selected_slugs'] = selected_slugs
        ctx['selected_catechisms'] = Catechism.objects.filter(slug__in=selected_slugs)
        ctx['docs_param'] = ','.join(selected_slugs)

        # Build prev/next navigation from the same custom theme set
        all_matching_themes = self._get_all_custom_themes(selected_slugs, active_traditions)
        current_idx = None
        for i, t in enumerate(all_matching_themes):
            if t['theme'].slug == theme_slug:
                current_idx = i
                break
        if current_idx is not None:
            ctx['previous_theme'] = all_matching_themes[current_idx - 1]['theme'] if current_idx > 0 else None
            if current_idx < len(all_matching_themes) - 1:
                ctx['next_theme'] = all_matching_themes[current_idx + 1]['theme']
            else:
                ctx['next_theme'] = None

        return ctx

    def _get_all_custom_themes(self, selected_slugs, active_traditions=None):
        """Get the full ordered list of themes for these selected documents."""
        if active_traditions is None:
            active_traditions = get_active_traditions(self.request)
        themes_with_matches = ComparisonTheme.objects.filter(
            entries__catechism__slug__in=selected_slugs,
            entries__catechism__tradition__in=active_traditions,
        ).distinct().prefetch_related(
            Prefetch(
                'entries',
                queryset=ComparisonEntry.objects.filter(
                    catechism__slug__in=selected_slugs,
                    catechism__tradition__in=active_traditions,
                ),
                to_attr='matching_entries'
            )
        )

        slug_groups = defaultdict(list)
        for theme in themes_with_matches:
            slug_groups[theme.slug].append(theme)

        result = []
        for slug, theme_list in slug_groups.items():
            matched_cats = set()
            for theme in theme_list:
                for entry in theme.matching_entries:
                    matched_cats.add(entry.catechism_id)
            if len(matched_cats) >= 2:
                result.append({
                    'theme': theme_list[0],
                    'locus': theme_list[0].locus,
                })

        result.sort(key=lambda x: (x['locus'], x['theme'].order))
        return result


class CompareSetView(ListView):
    template_name = 'catechism/compare_list.html'
    context_object_name = 'themes'

    def get(self, request, *args, **kwargs):
        try:
            self.comparison_set = ComparisonSet.objects.get(slug=kwargs['set_slug'])
        except ComparisonSet.DoesNotExist:
            # Legacy redirect: treat as old Westminster theme slug
            theme = get_object_or_404(
                ComparisonTheme,
                slug=kwargs['set_slug'],
                comparison_set__slug='westminster',
            )
            return redirect(theme.get_absolute_url(), permanent=True)

        # Block access to sets that reference catechisms outside supported
        # traditions (e.g. tradition='other')

        has_unsupported = ComparisonEntry.objects.filter(
            theme__comparison_set=self.comparison_set
        ).exclude(
            catechism__tradition__in=VALID_TRADITIONS
        ).exists()
        if has_unsupported:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        active_traditions = get_active_traditions(self.request)
        return self.comparison_set.themes.filter(
            entries__catechism__tradition__in=active_traditions
        ).annotate(
            entry_count=Count('entries', distinct=True)
        ).distinct().order_by('order')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comparison_set'] = self.comparison_set
        return ctx


class CompareSetThemeView(DetailView):
    template_name = 'catechism/compare_theme.html'
    context_object_name = 'theme'

    def get_object(self):
        theme = get_object_or_404(
            ComparisonTheme,
            slug=self.kwargs['theme_slug'],
            comparison_set__slug=self.kwargs['set_slug'],
        )
        # Block access to themes in sets that reference catechisms
        # outside supported traditions (e.g. tradition='other')

        has_unsupported = ComparisonEntry.objects.filter(
            theme__comparison_set=theme.comparison_set
        ).exclude(
            catechism__tradition__in=VALID_TRADITIONS
        ).exists()
        if has_unsupported:
            raise Http404
        return theme

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        entries = self.object.entries.filter(
            catechism__tradition__in=active_traditions
        ).select_related('catechism')
        ctx['columns'] = _build_columns(entries)
        ctx['comparison_set'] = self.object.comparison_set

        # Prev/next theme navigation within the same set (filtered to active traditions)
        all_themes = list(
            self.object.comparison_set.themes.filter(
                entries__catechism__tradition__in=active_traditions
            ).distinct().order_by('order')
        )
        current_idx = None
        for i, t in enumerate(all_themes):
            if t.pk == self.object.pk:
                current_idx = i
                break
        if current_idx is not None:
            ctx['previous_theme'] = all_themes[current_idx - 1] if current_idx > 0 else None
            ctx['next_theme'] = all_themes[current_idx + 1] if current_idx < len(all_themes) - 1 else None

        return ctx


def question_preview_json(request, pk):
    """Return lightweight JSON for the see-also preview panel."""
    active_traditions = get_active_traditions(request)
    q = get_object_or_404(
        Question.objects.select_related('catechism'),
        pk=pk,
        catechism__tradition__in=active_traditions,
    )
    response = JsonResponse({
        'catechism_name': q.catechism.name,
        'abbreviation': q.catechism.abbreviation,
        'item_prefix': q.catechism.item_prefix,
        'display_number': q.display_number,
        'is_confession': q.catechism.is_confession,
        'question_text': q.question_text,
        'answer_text': q.answer_text,
        'url': q.get_absolute_url(),
    })
    response['Cache-Control'] = 'no-store'
    return response


# Legacy redirects
class LegacyQuestionRedirect(View):
    def get(self, request, number):
        return redirect('catechism:question_detail',
                        catechism_slug='wsc', number=number, permanent=True)


class LegacyTopicRedirect(View):
    def get(self, request, slug):
        return redirect('catechism:topic_detail',
                        catechism_slug='wsc', slug=slug, permanent=True)
