import json
from collections import defaultdict
from datetime import date

from django.db.models import Q, Count, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .models import (
    Catechism, Topic, Question, Commentary, FisherSubQuestion,
    ScripturePassage, StandardCrossReference,
    BibleBook, ScriptureIndex, ComparisonSet, ComparisonTheme,
    ComparisonEntry,
)


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
        catechisms = list(Catechism.objects.all())
        day_of_year = date.today().timetuple().tm_yday
        for cat in catechisms:
            cat.featured_question = Question.objects.filter(
                catechism=cat,
                number=(day_of_year % cat.total_questions) + 1
            ).select_related('topic').first()
        ctx['catechisms'] = catechisms
        hero_cat = catechisms[day_of_year % len(catechisms)]
        ctx['featured'] = hero_cat.featured_question
        return ctx


class CatechismHomeView(CatechismMixin, TemplateView):
    template_name = 'catechism/catechism_home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
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
                )
            ),
            catechism=self.catechism,
            number=self.kwargs['number']
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.object
        ctx['previous_question'] = q.get_previous()
        ctx['next_question'] = q.get_next()

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

        # Generic cross-references (any catechism to any catechism)
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
            cross_ref_groups[other.catechism.abbreviation].append(other)

        # Sort each group by question number and cap display size
        MAX_CROSSREFS_PER_GROUP = 8
        for abbr in cross_ref_groups:
            cross_ref_groups[abbr].sort(key=lambda x: x.number)
            if len(cross_ref_groups[abbr]) > MAX_CROSSREFS_PER_GROUP:
                cross_ref_groups[abbr] = cross_ref_groups[abbr][:MAX_CROSSREFS_PER_GROUP]

        ctx['cross_ref_groups'] = dict(cross_ref_groups)

        # Comparison themes that include this question
        ctx['comparison_themes'] = ComparisonTheme.objects.filter(
            entries__catechism=q.catechism,
            entries__question_start__lte=q.number,
            entries__question_end__gte=q.number,
        )

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
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Question.objects.none()

        qs = Question.objects.filter(
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query)
        ).distinct().select_related('topic', 'catechism')

        catechism_slug = self.request.GET.get('catechism', '')
        if catechism_slug:
            qs = qs.filter(catechism__slug=catechism_slug)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['catechisms'] = Catechism.objects.all()
        return ctx


class ScriptureIndexView(TemplateView):
    template_name = 'catechism/scripture_index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        books = BibleBook.objects.annotate(
            citation_count=Count('index_entries')
        )
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
        entries = ScriptureIndex.objects.filter(
            book=self.object
        ).select_related('question__catechism', 'question__topic')

        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry.question.catechism.abbreviation].append({
                'question': entry.question,
                'reference': entry.reference,
            })

        ctx['grouped_entries'] = dict(grouped)
        ctx['total_citations'] = entries.count()
        return ctx


class CompareIndexView(ListView):
    template_name = 'catechism/compare_index.html'
    model = ComparisonSet
    context_object_name = 'comparison_sets'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['all_catechisms'] = Catechism.objects.all()
        # Build preset map: set slug → list of catechism slugs (for JS)
        preset_map = {}
        for cs in ctx['comparison_sets']:
            cat_slugs = list(
                ComparisonEntry.objects.filter(
                    theme__comparison_set=cs
                ).values_list(
                    'catechism__slug', flat=True
                ).distinct()
            )
            preset_map[cs.slug] = {
                'name': cs.name,
                'catechisms': cat_slugs,
            }
        ctx['preset_map_json'] = json.dumps(preset_map)
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

        # Parse document slugs from query parameter
        docs_param = self.request.GET.get('docs', '')
        selected_slugs = [s.strip() for s in docs_param.split(',') if s.strip()]

        # Validate against existing catechisms
        all_catechisms = Catechism.objects.all()
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

        docs_param = self.request.GET.get('docs', '')
        selected_slugs = [s.strip() for s in docs_param.split(',') if s.strip()]
        theme_slug = self.kwargs['theme_slug']

        # Find all themes with this slug across all sets
        themes = ComparisonTheme.objects.filter(slug=theme_slug)
        if not themes.exists():
            raise Http404

        primary_theme = themes.first()
        ctx['theme'] = primary_theme

        # Collect entries from all themes with this slug, filtered to selected docs
        all_entries = ComparisonEntry.objects.filter(
            theme__slug=theme_slug,
            catechism__slug__in=selected_slugs,
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
        all_matching_themes = self._get_all_custom_themes(selected_slugs)
        current_idx = None
        for i, t in enumerate(all_matching_themes):
            if t['theme'].slug == theme_slug:
                current_idx = i
                break
        if current_idx is not None:
            ctx['previous_theme'] = all_matching_themes[current_idx - 1]['theme'] if current_idx > 0 else None
            ctx['next_theme'] = all_matching_themes[current_idx + 1]['theme'] if current_idx < len(all_matching_themes) - 1 else None

        return ctx

    def _get_all_custom_themes(self, selected_slugs):
        """Get the full ordered list of themes for these selected documents."""
        themes_with_matches = ComparisonTheme.objects.filter(
            entries__catechism__slug__in=selected_slugs
        ).distinct().prefetch_related(
            Prefetch(
                'entries',
                queryset=ComparisonEntry.objects.filter(
                    catechism__slug__in=selected_slugs
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
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.comparison_set.themes.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comparison_set'] = self.comparison_set
        return ctx


class CompareSetThemeView(DetailView):
    template_name = 'catechism/compare_theme.html'
    context_object_name = 'theme'

    def get_object(self):
        return get_object_or_404(
            ComparisonTheme,
            slug=self.kwargs['theme_slug'],
            comparison_set__slug=self.kwargs['set_slug'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        entries = self.object.entries.select_related('catechism').all()
        ctx['columns'] = _build_columns(entries)
        ctx['comparison_set'] = self.object.comparison_set

        # Prev/next theme navigation within the same set
        all_themes = list(self.object.comparison_set.themes.all())
        current_idx = None
        for i, t in enumerate(all_themes):
            if t.pk == self.object.pk:
                current_idx = i
                break
        if current_idx is not None:
            ctx['previous_theme'] = all_themes[current_idx - 1] if current_idx > 0 else None
            ctx['next_theme'] = all_themes[current_idx + 1] if current_idx < len(all_themes) - 1 else None

        return ctx


# Legacy redirects
class LegacyQuestionRedirect(View):
    def get(self, request, number):
        return redirect('catechism:question_detail',
                        catechism_slug='wsc', number=number, permanent=True)


class LegacyTopicRedirect(View):
    def get(self, request, slug):
        return redirect('catechism:topic_detail',
                        catechism_slug='wsc', slug=slug, permanent=True)
