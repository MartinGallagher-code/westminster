from collections import defaultdict
from urllib.parse import quote, urlencode
from datetime import date
from xml.sax.saxutils import escape

from django.db import connection
from django.db.models import Q, Count, Prefetch, F
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django_ratelimit.decorators import ratelimit

from .atlas import atlas_url
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
from .cache import cache_read_only_page
from .diffing import align_columns, build_diff, change_ratio, diff_words, section_text
from .citations import bibtex, citation_label, citation_text, resolve_reference, ris
from .handout import build_handout
from .scripture_refs import (
    chapter_from_ref, parse_scripture_reference, reference_matches_chapter,
    scripture_urls,
)
from .search_text import search_terms as _search_terms
from .utils import DEFAULT_TRADITIONS, VALID_TRADITIONS, get_active_traditions

# Search results were rendered in full, every match on one page: "the" returned
# 633KB of HTML and "God" 282KB. Across documents each group now shows a sample
# and offers the rest behind its own filter; within one document the list pages.
GROUPED_SEARCH_SAMPLE = 10
SEARCH_PAGE_SIZE = 25


# Curated quick-start groupings for the custom comparison selector. Each preset
# is filtered against the documents currently available in the active
# traditions, so a preset only appears when at least two of its documents are
# available to compare.
COMPARISON_PRESETS = [
    {
        'name': 'Westminster Standards',
        'slugs': ['wcf', 'wlc', 'wsc'],
        'description': 'The Confession of Faith with the Larger and Shorter Catechisms.',
    },
    {
        'name': 'Three Forms of Unity',
        'slugs': ['heidelberg', 'belgic', 'dort'],
        'description': 'The Heidelberg Catechism, Belgic Confession, and Canons of Dort.',
    },
    {
        'name': 'Confessional Lineage',
        'slugs': ['wcf', 'savoy', '1689'],
        'description': (
            'Westminster (1646) to Savoy (1658) to the Second London Baptist '
            'Confession (1689) — Presbyterian to Congregationalist to Baptist.'
        ),
    },
    {
        'name': 'Pre-Westminster',
        'slugs': ['scots', 'second-helvetic', 'irish', 'wcf'],
        'description': (
            'The Scots Confession (1560), Second Helvetic (1566), and Irish '
            'Articles (1615) beside the Confession they shaped.'
        ),
    },
]


def _available_comparison_presets(available_slugs):
    """Return presets restricted to available documents, keeping only those
    that still cover at least two documents."""
    available = set(available_slugs)
    presets = []
    for preset in COMPARISON_PRESETS:
        slugs = [s for s in preset['slugs'] if s in available]
        if len(slugs) >= 2:
            presets.append({
                'name': preset['name'],
                'description': preset['description'],
                'slugs': slugs,
                'docs_param': ','.join(slugs),
            })
    return presets


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
    ).exclude(
        # A theme is only reachable if its whole comparison set is reachable:
        # CompareSetThemeView 404s every theme in a set that references an
        # unsupported tradition, so a theme that happens to carry only
        # supported entries (e.g. the 1689 set's "Of Church Government", whose
        # 1689/Savoy ranges are null) must not be advertised in the sitemap or
        # linked from the doctrine index. Mirrors _comparison_sets_for_traditions.
        comparison_set__themes__entries__catechism__tradition=Catechism.OTHER
    ).annotate(
        active_entry_count=Count(
            'entries',
            filter=Q(entries__catechism__tradition__in=active_traditions),
            distinct=True,
        )
    ).select_related('comparison_set').distinct()


def _comparison_themes_for_topic(topic, active_traditions):
    """Reachable comparison themes whose entry for this document covers this chapter.

    A comparison set aligns chapter ranges, not chapters, so the match is an
    overlap test rather than equality: the 1689 folds WCF XXV and XXVI into one
    chapter, and both should offer the comparison.

    Ordered so the most useful comparison comes first: how much of the chapter
    the theme covers, then whether the documents it sets alongside this one are
    the same kind of text. Without that second key WCF II leads with the
    Westminster set, whose parallels are catechism answers — a fair comparison,
    but not a word-level one, and the diff of a chapter against a Q&A is noise.
    """
    themes = list(
        _comparison_themes_for_traditions(active_traditions).filter(
            entries__catechism=topic.catechism,
            entries__question_start__lte=topic.question_end,
            entries__question_end__gte=topic.question_start,
            active_entry_count__gte=2,
        ).order_by('comparison_set__order', 'order')
    )
    if not themes:
        return []

    spans = {}
    same_kind = set()
    for entry in ComparisonEntry.objects.filter(
        theme__in=themes, catechism__tradition__in=active_traditions,
    ).select_related('catechism'):
        if entry.catechism_id == topic.catechism_id:
            spans[entry.theme_id] = (entry.question_start, entry.question_end)
        elif entry.catechism.is_prose_document == topic.catechism.is_prose_document:
            same_kind.add(entry.theme_id)

    def rank(pair):
        index, theme = pair
        start, end = spans.get(theme.pk, (0, -1))
        overlap = min(end, topic.question_end) - max(start, topic.question_start) + 1
        return (-overlap, theme.pk not in same_kind, index)

    return [theme for _, theme in sorted(enumerate(themes), key=rank)]


def _dormant_comparison_traditions(topic, active_traditions):
    """Collections that treat this chapter but are switched off for this reader.

    A reader with only the Westminster Standards enabled sees no comparison at
    all on WCF XXV, because the documents that revise it — the Savoy and the
    1689 — sit in a collection they have not turned on. The site knows they
    exist; saying so is more use than an empty space.
    """
    dormant = {
        tradition for tradition in VALID_TRADITIONS
        if tradition not in active_traditions
    }
    if not dormant:
        return []

    # Ask with every collection on, so this reports only what turning one on
    # would actually reach — the same reachability rules as the panel itself.
    themes = _comparison_themes_for_topic(topic, sorted(VALID_TRADITIONS))
    if not themes:
        return []

    labels = dict(Catechism.TRADITION_CHOICES)
    documents = {}
    for entry in ComparisonEntry.objects.filter(
        theme__in=themes, catechism__tradition__in=dormant,
    ).select_related('catechism'):
        documents.setdefault(entry.catechism.tradition, {})[
            entry.catechism.abbreviation
        ] = entry.catechism

    return [
        {
            'tradition': tradition,
            'label': labels.get(tradition, tradition),
            'documents': [found[key] for key in sorted(found)],
        }
        for tradition, found in sorted(documents.items())
    ]


# A query matching a topic name pulls in that topic's questions too. Bounded
# so a one-letter query cannot build an unbounded id array.
MAX_TOPIC_MATCH_IDS = 500


def _search_questions(query, active_traditions):
    base_qs = Question.objects.filter(
        catechism__tradition__in=active_traditions
    ).select_related('topic', 'catechism')
    terms = _search_terms(query)

    if connection.vendor == 'postgresql':
        # Match against the stored, GIN-indexed search_vector column added in
        # migration 0023 rather than building a tsvector per row per query.
        # The column lives in the database only — declaring it as a model field
        # would break every SQLite migration — so the condition is raw SQL
        # against the real table name, which no join alias can shift.
        from django.db.models.expressions import RawSQL

        tsquery = "websearch_to_tsquery('english', %s)"
        # Topic names live in another table, so they cannot go in the generated
        # column. Resolving them to ids first keeps the OR between two
        # index-backed conditions — the GIN index on search_vector and the
        # primary key — which a subquery in the OR would have ruled out.
        topic_question_ids = list(
            Question.objects.filter(topic__name__icontains=query)
            .values_list('id', flat=True)[:MAX_TOPIC_MATCH_IDS]
        )
        return base_qs.annotate(
            rank=RawSQL(
                f'ts_rank(catechism_question.search_vector, {tsquery})', (query,),
            ),
        ).extra(
            where=[
                f'(catechism_question.search_vector @@ {tsquery}'
                ' OR catechism_question.id = ANY(%s))'
            ],
            params=[query, topic_question_ids],
        ).order_by('-rank', 'catechism__abbreviation', 'number')

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
        # Public explainer for signed-out visitors, so it is discoverable.
        reverse('accounts:memorize'),
    ]

    supported_catechisms = Catechism.objects.filter(
        tradition__in=VALID_TRADITIONS
    ).prefetch_related('topics', 'questions').order_by('tradition', 'abbreviation')
    for catechism in supported_catechisms:
        urls.append(catechism.get_absolute_url())
        urls.extend(topic.get_absolute_url() for topic in catechism.topics.all())
        urls.extend(question.get_absolute_url() for question in catechism.questions.all())

    urls.extend(book.get_absolute_url() for book in BibleBook.objects.all())

    # Comparison and doctrine pages are gated on the *visitor's* active
    # traditions, and a crawler sends no docFilters cookie — so advertise only
    # what resolves under DEFAULT_TRADITIONS. Listing more means listing 404s
    # (e.g. /doctrine/of-the-gospel/, whose only entries are 1689 and Savoy).
    urls.extend(
        comparison_set.get_absolute_url()
        for comparison_set in _comparison_sets_for_traditions(DEFAULT_TRADITIONS)
    )

    comparison_themes = _comparison_themes_for_traditions(DEFAULT_TRADITIONS)
    urls.extend(theme.get_absolute_url() for theme in comparison_themes)
    urls.extend(
        reverse('catechism:doctrine_detail', kwargs={'theme_slug': slug})
        for slug in comparison_themes.values_list('slug', flat=True).distinct()
    )

    # The Atlas's own pages (ontology, personas, cruxes, schools, heads).
    from westminster_standards.sitemap import atlas_sitemap_paths
    urls.extend(atlas_sitemap_paths())

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

        # Each document shows a question of the day. Asking for them one at a
        # time cost a query per document — twelve on a home page that is
        # otherwise six — so ask for all of them at once.
        wanted = {
            cat.id: (day_of_year % cat.total_questions) + 1
            for cat in catechisms if cat.total_questions
        }
        featured = {}
        if wanted:
            lookup = Q()
            for catechism_id, number in wanted.items():
                lookup |= Q(catechism_id=catechism_id, number=number)
            featured = {
                question.catechism_id: question
                for question in Question.objects.filter(lookup).select_related('topic')
            }
        for cat in catechisms:
            cat.featured_question = featured.get(cat.id)
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
            from accounts.models import MemorizationCard, ReadingPosition, UserNote
            ctx['recent_note'] = UserNote.objects.filter(
                user=self.request.user
            ).select_related(
                'question', 'question__catechism', 'question__topic'
            ).order_by('-updated_at').first()

            # Where you were, what is due, what to read next — the three
            # things a returning reader wants before they want anything else.
            ctx['reading_positions'] = list(
                ReadingPosition.objects.filter(user=self.request.user)
                .select_related('question', 'question__catechism', 'question__topic')[:3]
            )
            ctx['memorisation_due'] = MemorizationCard.objects.filter(
                user=self.request.user, due_on__lte=date.today(),
            ).count()
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
        ctx['featured_question'] = None
        if self.catechism.total_questions:
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
        from .atlas import comparison_locus_atlas
        ctx['locus_groups'] = [
            {'locus': locus, 'themes': items, 'atlas': comparison_locus_atlas(locus)}
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


@method_decorator(cache_read_only_page, name='dispatch')
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
        # A per-reference fallback used to follow this, re-querying each
        # reference the bulk lookup did not return. It is the same exact-match
        # filter, so it could never find anything: over 400 questions it
        # rescued none of 2,148 misses, at the cost of one query apiece.
        ctx['scripture_map'] = {
            p.reference: p.text
            for p in ScripturePassage.objects.filter(reference__in=refs)
        } if refs else {}
        # Verse text is fetched from an external service (``fetch_scripture``)
        # and is often absent, but the reference itself always has somewhere to
        # go: the Scripture index knows every question that cites the passage.
        ctx['scripture_link_map'] = scripture_urls(refs)

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

        # Chapter mode shows each section's question and answer, not its proof
        # apparatus, so no per-chapter scripture map is built. One used to be —
        # a passage query over every section's references on every question page
        # — feeding a `chapter_scripture_map` no template ever read.

        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            from accounts.forms import NoteForm
            from accounts.models import MemorizationCard, ReadingPosition
            ReadingPosition.remember(self.request.user, q)
            ctx['user_note'] = UserNote.objects.filter(
                user=self.request.user, question=q
            ).first()
            ctx['note_form'] = NoteForm()
            ctx['memorization_card'] = MemorizationCard.objects.filter(
                user=self.request.user, question=q
            ).first()

        ctx['citation_reference'] = q.display_number
        ctx['citation_label'] = citation_label(q)
        ctx['citation_text'] = citation_text(
            q, self.request.build_absolute_uri(reverse('catechism:citation_permalink', kwargs={
                'catechism_slug': q.catechism.slug, 'reference': q.display_number,
            })),
        )

        return ctx


class TopicListRedirectView(CatechismMixin, View):
    """Redirect old topic/chapter list to the home page."""

    def get(self, request, *args, **kwargs):
        return redirect(self.catechism.get_absolute_url())


@method_decorator(cache_read_only_page, name='dispatch')
class TopicDetailView(CatechismMixin, DetailView):
    template_name = 'catechism/topic_detail.html'
    context_object_name = 'topic'

    def get_object(self):
        return get_object_or_404(
            Topic, catechism=self.catechism, slug=self.kwargs['slug']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # display_number reads each question's topic; without this that was a
        # query per section of the chapter.
        ctx['questions'] = Question.objects.filter(
            catechism=self.catechism, topic=self.object
        ).select_related('topic')
        from .atlas import topic_loci
        ctx['atlas_loci'] = topic_loci(self.object)

        # Every chapter of a confession is a revision of, or a reply to,
        # somebody else's chapter. The comparison sets already know which —
        # this surfaces the link from the chapter itself, rather than only
        # from the comparison index a reader has to go looking for.
        active_traditions = get_active_traditions(self.request)
        themes = _comparison_themes_for_topic(self.object, active_traditions)
        ctx['comparison_themes'] = themes
        ctx['dormant_comparison_traditions'] = _dormant_comparison_traditions(
            self.object, active_traditions
        )
        if themes:
            others = [
                entry.catechism for entry in _order_entries_chronologically(
                    themes[0].entries.filter(
                        catechism__tradition__in=active_traditions
                    ).select_related('catechism')
                )
                if entry.catechism_id != self.object.catechism_id
            ]
            ctx['primary_comparison_theme'] = themes[0]
            ctx['primary_comparison_documents'] = others
            # A word-level diff is only worth offering against a document of
            # the same kind. WCF I against the Savoy's chapter I shows the
            # handful of edits; WCF I against WSC Q2 is two different texts,
            # and the diff would report every word as changed.
            ctx['primary_comparison_diff_target'] = next(
                (
                    document for document in others
                    if document.is_prose_document == self.object.catechism.is_prose_document
                ),
                None,
            )
        return ctx


# Search is the most expensive read on the site and the obvious scraping
# target. The limit is per-IP and deliberately generous: church and library
# networks share an address.
@method_decorator(ratelimit(key='ip', rate='120/m', method='GET', block=True), name='get')
class SearchView(ListView):
    template_name = 'catechism/search_results.html'
    context_object_name = 'results'

    def get(self, request, *args, **kwargs):
        # "Rom 8:30" is a request for the Scripture index, not a substring
        # search over question text. ?text=1 opts back into the text search.
        if not request.GET.get('text'):
            reference = parse_scripture_reference(request.GET.get('q', ''))
            if reference:
                destination = reference['book'].get_absolute_url()
                params = urlencode({
                    'ref': reference['ref'],
                    'from': request.GET.get('q', '').strip(),
                })
                return redirect(f'{destination}?{params}')
        return super().get(request, *args, **kwargs)

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

    def get_paginate_by(self, queryset):
        """Paginate a single document's results; sample across many.

        Filtered to one document, the reader wants the whole list and pages
        through it. Unfiltered, the page's job is to show which documents
        answer to the word at all, so it samples each group instead (see
        ``get_context_data``) and paging would only obscure that.
        """
        return SEARCH_PAGE_SIZE if self.request.GET.get('catechism') else None

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

        # Site search also reaches into the Atlas layers that have no
        # counterpart in the standards' text — its divines, cruxes, schools,
        # and heads of doctrine — so one search covers the whole site.
        from westminster_standards.entity_search import search_entities
        ctx['atlas_results'] = search_entities(ctx['query'])
        ctx['atlas_total'] = sum(group['total'] for group in ctx['atlas_results'])

        tradition_order = {
            'westminster': 0, 'three_forms_of_unity': 1,
            'reformed_confessions': 2, 'other': 3,
        }
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
        # When paginated, ``results`` is one page of objects, so the true count
        # comes from the paginator rather than from what this page rendered.
        paginator = ctx.get('paginator')
        ctx['total_results'] = (
            paginator.count if paginator else sum(len(qs) for qs in grouped.values())
        )

        # Across every document, show a sample per document rather than the lot:
        # the value of the unfiltered page is knowing *which* documents answer
        # to the word, and "the" used to render 633KB of every match in one
        # scroll. Each group offers the rest behind its own document filter,
        # which is where the reader gets real pagination — and where the whole
        # page is already one document's worth, so nothing is held back.
        ctx['grouped_results'] = [
            {
                'catechism': cat,
                'questions': (
                    grouped[cat.pk] if paginator
                    else grouped[cat.pk][:GROUPED_SEARCH_SAMPLE]
                ),
                'total': paginator.count if paginator else len(grouped[cat.pk]),
                'has_more': (
                    not paginator and len(grouped[cat.pk]) > GROUPED_SEARCH_SAMPLE
                ),
                'more_url': (
                    f"{reverse('catechism:search')}"
                    f"?{urlencode({'q': ctx['query'], 'catechism': cat.slug})}"
                ),
            }
            for cat in ordered_cats
        ]
        # Carried on every pagination link so paging does not drop the filter.
        ctx['pagination_query'] = urlencode({
            k: v for k, v in (
                ('q', ctx['query']),
                ('catechism', ctx['selected_catechism_slug']),
            ) if v
        })
        # The Atlas matches are the same on every page; repeating them under
        # each page of a filtered search is noise.
        ctx['show_atlas_results'] = not paginator or ctx['page_obj'].number == 1
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


@method_decorator(cache_read_only_page, name='dispatch')
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

        # Arriving from a search for "Rom 8:30": narrow to that chapter, but
        # fall back to the whole book rather than showing an empty page.
        requested_ref = self.request.GET.get('ref', '')
        chapter = chapter_from_ref(requested_ref)
        entries = list(entries)
        if chapter is not None:
            in_chapter = [
                entry for entry in entries
                if reference_matches_chapter(entry.reference, chapter)
            ]
            ctx['filtered_ref'] = f'{self.object.name} {requested_ref}'
            ctx['filtered_chapter'] = chapter
            ctx['filter_found_nothing'] = not in_chapter
            if in_chapter:
                entries = in_chapter
        ctx['search_fallback_query'] = self.request.GET.get('from', '')

        grouped = defaultdict(list)
        catechism_map = {}
        for entry in entries:
            cat = entry.question.catechism
            grouped[cat.pk].append({'question': entry.question, 'reference': entry.reference})
            catechism_map[cat.pk] = cat

        tradition_order = {
            'westminster': 0, 'three_forms_of_unity': 1,
            'reformed_confessions': 2, 'other': 3,
        }
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
        all_catechisms = Catechism.objects.filter(
            tradition__in=active_traditions,
            comparison_entries__isnull=False,
        ).distinct()
        ctx['all_catechisms'] = all_catechisms
        ctx['active_traditions'] = active_traditions
        ctx['comparison_presets'] = _available_comparison_presets(
            all_catechisms.values_list('slug', flat=True)
        )
        return ctx


def _order_entries_chronologically(entries):
    """Oldest document first.

    The default ordering is alphabetical by abbreviation, which puts the 1689
    before the Confession it revises. These sets are read left-to-right as a
    lineage, so order by the document's year and fall back to the abbreviation
    when a year is missing.
    """
    return entries.order_by(
        F('catechism__year').asc(nulls_last=True), 'catechism__abbreviation',
    )


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

        if len(selected_slugs) < 2:
            ctx['columns'] = []
            ctx['selected_slugs'] = selected_slugs
            ctx['selected_catechisms'] = Catechism.objects.filter(slug__in=selected_slugs)
            ctx['docs_param'] = ','.join(selected_slugs)
            ctx['error'] = 'Select at least two documents to compare.'
            return ctx

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


@method_decorator(cache_read_only_page, name='dispatch')
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
        entries = _order_entries_chronologically(
            self.object.entries.filter(
                catechism__tradition__in=active_traditions
            ).select_related('catechism')
        )
        ctx['columns'] = _build_columns(entries)
        ctx['comparison_set'] = self.object.comparison_set

        # Documents in this set that have no parallel for this theme. The
        # absence is itself informative — the 1689 has no chapter answering
        # WCF XXXI, for instance — so name them rather than silently showing
        # a narrower table.
        covered = {entry.catechism_id for entry in entries}
        ctx['documents_without_entry'] = [
            catechism for catechism in Catechism.objects.filter(
                comparison_entries__theme__comparison_set=self.object.comparison_set,
                tradition__in=active_traditions,
            ).distinct()
            if catechism.id not in covered
        ]

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


# ── Citations ─────────────────────────────────────────────────────────────


def _resolve_citation(catechism_slug, reference):
    """The question a '/cite/<doc>/<reference>/' URL denotes, or 404."""
    catechism = get_object_or_404(Catechism, slug=catechism_slug)
    question = resolve_reference(catechism, reference)
    if question is None:
        raise Http404(f'No {catechism.abbreviation} {reference}')
    return question


class CitationPermalinkView(View):
    """'/cite/wcf/3.4/' — the reference a reader actually writes.

    Redirects to the canonical page, whose URL is built from the sequential
    question number and so cannot be derived from a citation by hand.
    """

    def get(self, request, catechism_slug, reference):
        question = _resolve_citation(catechism_slug, reference)
        return redirect(question.get_absolute_url(), permanent=True)


class CitationExportView(View):
    """Download one section or question as BibTeX or RIS."""

    FORMATS = {
        'bibtex': (bibtex, 'application/x-bibtex', 'bib'),
        'ris': (ris, 'application/x-research-info-systems', 'ris'),
    }

    def get(self, request, catechism_slug, reference, fmt):
        if fmt not in self.FORMATS:
            raise Http404(f'Unknown citation format {fmt!r}')
        question = _resolve_citation(catechism_slug, reference)
        render_citation, content_type, extension = self.FORMATS[fmt]

        permalink = request.build_absolute_uri(
            reverse('catechism:citation_permalink', kwargs={
                'catechism_slug': catechism_slug, 'reference': reference,
            })
        )
        body = render_citation(question, url=permalink, accessed=date.today())
        response = HttpResponse(body, content_type=f'{content_type}; charset=utf-8')
        filename = f'{catechism_slug}-{reference.replace(".", "-")}.{extension}'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@method_decorator(cache_read_only_page, name='dispatch')
class HandoutView(TemplateView):
    """A print-ready session handout for a question, section, or whole chapter.

    Rendered as a page rather than a server-generated PDF: every browser
    prints to PDF, and a page keeps the links live for anyone reading it on a
    screen.
    """

    template_name = 'catechism/handout.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        catechism = get_object_or_404(Catechism, slug=self.kwargs['catechism_slug'])
        reference = self.kwargs.get('reference')
        topic_slug = self.kwargs.get('topic_slug')

        if topic_slug:
            topic = get_object_or_404(Topic, catechism=catechism, slug=topic_slug)
            questions = list(
                topic.questions.select_related('catechism', 'topic').order_by('number')
            )
            ctx['heading'] = topic.name
            ctx['subheading'] = (
                f'{catechism.name} · {catechism.item_prefix}{topic.display_start}'
                f'–{catechism.item_prefix}{topic.display_end}'
            )
            ctx['topic'] = topic
        else:
            question = resolve_reference(catechism, reference)
            if question is None:
                raise Http404(f'No {catechism.abbreviation} {reference}')
            questions = [question]
            ctx['heading'] = f'{catechism.abbreviation} {question.display_number}'
            ctx['subheading'] = catechism.name

        ctx['catechism'] = catechism
        ctx['items'] = build_handout(questions)
        ctx['generated_on'] = date.today()
        return ctx


class ParallelReadView(TemplateView):
    """Read the editions in lockstep, section against section.

    The comparison page sets the documents beside one another but lets each
    column flow at its own length, so by the third section the Savoy is level
    with the Confession's fourth and the reader is comparing the wrong things.
    The alignment the diff already relies on fixes that: one row per section,
    every edition level, so scrolling one scrolls all of them.
    """

    template_name = 'catechism/compare_parallel.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)

        theme = get_object_or_404(
            ComparisonTheme,
            slug=self.kwargs['theme_slug'],
            comparison_set__slug=self.kwargs['set_slug'],
        )
        # Same gate as the comparison page it is reached from.
        if ComparisonEntry.objects.filter(
            theme__comparison_set=theme.comparison_set
        ).exclude(catechism__tradition__in=VALID_TRADITIONS).exists():
            raise Http404

        entries = list(
            _order_entries_chronologically(
                theme.entries.filter(
                    catechism__tradition__in=active_traditions
                ).select_related('catechism')
            )
        )

        # ?docs= narrows the columns. Four editions side by side is a wall;
        # a reader chasing one revision wants two. Accepts both the repeated
        # form the checkbox picker submits and the comma-separated form that
        # makes a shareable link.
        wanted = [
            slug
            for value in self.request.GET.getlist('docs')
            for slug in value.split(',') if slug
        ]
        if wanted:
            chosen = [entry for entry in entries if entry.catechism.slug in wanted]
            if chosen:
                entries = chosen

        ctx['theme'] = theme
        ctx['comparison_set'] = theme.comparison_set
        ctx['entries'] = entries
        ctx['documents'] = [entry.catechism for entry in entries]
        ctx['docs_param'] = ','.join(entry.catechism.slug for entry in entries)
        if len(entries) < 2:
            ctx['error'] = (
                'Reading in parallel needs two documents in your active '
                'collections.'
            )
            return ctx

        ctx['rows'] = self._rows(entries)
        ctx['edited_rows'] = sum(1 for row in ctx['rows'] if row['edited'])
        return ctx

    @staticmethod
    def _rows(entries):
        """One row per section, with each cell measured against the earliest
        edition that has a section there — so a reader can see at a glance
        which sections a later confession left alone."""
        rows = []
        columns = align_columns([list(entry.get_questions()) for entry in entries])
        for index, questions in enumerate(columns, start=1):
            baseline = next((q for q in questions if q is not None), None)
            baseline_text = section_text(baseline)
            cells = []
            for question in questions:
                if question is None:
                    cells.append({'question': None, 'status': 'absent'})
                elif question is baseline:
                    cells.append({'question': question, 'status': 'baseline'})
                else:
                    ratio = change_ratio(diff_words(baseline_text, section_text(question)))
                    cells.append({
                        'question': question,
                        'status': 'identical' if ratio == 0.0 else 'edited',
                        'change_ratio': ratio,
                        'change_percent': int(round(ratio * 100)),
                    })
            rows.append({
                'number': index,
                'cells': cells,
                'edited': any(cell['status'] == 'edited' for cell in cells),
                'absent': any(cell['status'] == 'absent' for cell in cells),
            })
        return rows


class CompareDiffView(TemplateView):
    """Word-level diff between two editions of the same chapter.

    The Savoy Declaration and the 1689 are revisions of the Confession; side by
    side they look identical and the edits are easy to miss. This shows what
    actually changed.
    """

    template_name = 'catechism/compare_diff.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)

        theme = get_object_or_404(
            ComparisonTheme,
            slug=self.kwargs['theme_slug'],
            comparison_set__slug=self.kwargs['set_slug'],
        )
        entries = list(
            _order_entries_chronologically(
                theme.entries.filter(
                    catechism__tradition__in=active_traditions,
                ).select_related('catechism')
            )
        )
        if len(entries) < 2:
            ctx['theme'] = theme
            ctx['comparison_set'] = theme.comparison_set
            ctx['error'] = (
                'This theme needs two documents in your active collections '
                'before it can be compared word by word.'
            )
            ctx['entries'] = entries
            return ctx

        by_slug = {entry.catechism.slug: entry for entry in entries}
        left_entry = by_slug.get(self.request.GET.get('a'), entries[0])
        right_entry = by_slug.get(self.request.GET.get('b'))
        if right_entry is None or right_entry == left_entry:
            right_entry = next(entry for entry in entries if entry != left_entry)

        ctx['theme'] = theme
        ctx['comparison_set'] = theme.comparison_set
        ctx['entries'] = entries
        ctx['left'] = left_entry.catechism
        ctx['right'] = right_entry.catechism
        ctx['rows'] = build_diff(left_entry.get_questions(), right_entry.get_questions())
        ctx['changed_rows'] = sum(1 for row in ctx['rows'] if not row['unchanged'])
        return ctx


# ── Unified suggestions ───────────────────────────────────────────────────

SUGGEST_MIN_LENGTH = 2
SUGGEST_PER_GROUP = 5


@method_decorator(ratelimit(key='ip', rate='240/m', method='GET', block=True), name='get')
class SearchSuggestView(View):
    """Typeahead across everything the site holds.

    Site search covered the standards' text and the Atlas had a search of its
    own, so a reader had to know the Atlas existed before they could find a
    divine or a position in it. One box, results grouped by what they are.
    """

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if len(query) < SUGGEST_MIN_LENGTH:
            return JsonResponse({'groups': []})

        groups = []

        reference = parse_scripture_reference(query)
        if reference:
            groups.append({'label': 'Scripture', 'items': [{
                'name': reference['label'],
                'detail': 'see where this passage is cited',
                'url': reference['book'].get_absolute_url() + f"?ref={reference['ref']}",
            }]})

        questions = _search_questions(
            query, get_active_traditions(request),
        ).select_related('catechism', 'topic')[:SUGGEST_PER_GROUP]
        if questions:
            groups.append({'label': 'In the standards', 'items': [
                {
                    'name': f'{q.catechism.abbreviation} {q.catechism.item_prefix}{q.display_number}',
                    'detail': q.question_text[:90],
                    'url': q.get_absolute_url(),
                }
                for q in questions
            ]})

        from westminster_standards.entity_search import search_entities
        for group in search_entities(query, limit=SUGGEST_PER_GROUP):
            groups.append({'label': group['label'], 'items': [
                {
                    'name': item['name'],
                    'detail': (item.get('description') or '')[:90],
                    'url': item['url'],
                }
                for item in group['items']
            ]})

        from westminster_standards.glossary import UNIQUE_BY_LABEL, url_for
        lowered = query.lower()
        positions = [
            entry for label, entry in UNIQUE_BY_LABEL.items()
            if lowered in label.lower()
        ][:SUGGEST_PER_GROUP]
        if positions:
            groups.append({'label': 'Positions', 'items': [
                {
                    'name': entry['label'],
                    'detail': entry['definition'][:90],
                    'url': url_for(entry),
                }
                for entry in positions
            ]})

        return JsonResponse({
            'groups': groups,
            'search_url': f"{reverse('catechism:search')}?q={quote(query)}",
        })


class PresenterView(TemplateView):
    """One question at a time, large, for a group looking at a screen.

    The handout covers paper; nothing covered projection. Deliberately
    chromeless: no navbar, no sidebar, no commentary — just the text, advanced
    from the keyboard or a clicker, which sends arrow keys.
    """

    template_name = 'catechism/presenter.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        catechism = get_object_or_404(Catechism, slug=self.kwargs['catechism_slug'])

        topic_slug = self.kwargs.get('topic_slug')
        if topic_slug:
            topic = get_object_or_404(Topic, catechism=catechism, slug=topic_slug)
            questions = list(topic.questions.order_by('number'))
            ctx['heading'] = topic.name
        else:
            first = int(self.request.GET.get('from', 1))
            last = int(self.request.GET.get('to', first))
            questions = list(
                catechism.questions.filter(number__gte=first, number__lte=last)
                .order_by('number')
            )
            ctx['heading'] = catechism.name

        if not questions:
            raise Http404('Nothing to present')

        ctx['catechism'] = catechism
        ctx['slides'] = [
            {
                'number': f'{catechism.item_prefix}{question.display_number}',
                'question': question.question_text,
                'answer': question.answer_text,
                'proofs': question.get_proof_text_list(),
                'url': question.get_absolute_url(),
            }
            for question in questions
        ]
        return ctx


class SessionPlanView(TemplateView):
    """Turn a chosen range into everything a group leader needs at once."""

    template_name = 'catechism/session_plan.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_traditions = get_active_traditions(self.request)
        ctx['catechisms'] = Catechism.objects.filter(
            tradition__in=active_traditions,
        ).order_by('abbreviation')

        slug = self.request.GET.get('catechism', '')
        catechism = Catechism.objects.filter(slug=slug).first()
        if catechism is None:
            return ctx

        topics = list(catechism.topics.order_by('order'))
        ctx['catechism'] = catechism
        ctx['topics'] = topics

        topic_slug = self.request.GET.get('topic', '')
        topic = next((t for t in topics if t.slug == topic_slug), None)
        if topic is None:
            return ctx

        ctx['topic'] = topic
        ctx['questions'] = topic.questions.order_by('number')
        ctx['plan'] = {
            'handout': reverse('catechism:handout_topic', kwargs={
                'catechism_slug': catechism.slug, 'topic_slug': topic.slug,
            }),
            'presenter': reverse('catechism:presenter_topic', kwargs={
                'catechism_slug': catechism.slug, 'topic_slug': topic.slug,
            }),
            'reading': topic.get_absolute_url(),
            'share': self.request.build_absolute_uri(),
        }
        return ctx
