from collections import defaultdict
from datetime import date

from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .models import (
    Catechism, Topic, Question, Commentary, FisherSubQuestion,
    ScripturePassage, StandardCrossReference,
    BibleBook, ScriptureIndex, ComparisonTheme,
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
        ctx['topics'] = Topic.objects.filter(catechism=self.catechism)
        ctx['question_count'] = Question.objects.filter(catechism=self.catechism).count()
        day_of_year = date.today().timetuple().tm_yday
        ctx['featured_question'] = Question.objects.filter(
            catechism=self.catechism,
            number=(day_of_year % self.catechism.total_questions) + 1
        ).select_related('topic').first()
        return ctx


class QuestionListView(CatechismMixin, ListView):
    template_name = 'catechism/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(
            catechism=self.catechism
        ).select_related('topic')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        topics = Topic.objects.filter(catechism=self.catechism)
        questions_by_topic = defaultdict(list)
        for q in ctx['questions']:
            questions_by_topic[q.topic_id].append(q)
        ctx['grouped'] = [
            {'topic': topic, 'questions': questions_by_topic.get(topic.id, [])}
            for topic in topics
        ]
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

        # Sort each group by question number
        for abbr in cross_ref_groups:
            cross_ref_groups[abbr].sort(key=lambda x: x.number)

        ctx['cross_ref_groups'] = dict(cross_ref_groups)

        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            from accounts.forms import NoteForm
            ctx['user_note'] = UserNote.objects.filter(
                user=self.request.user, question=q
            ).first()
            ctx['note_form'] = NoteForm()

        return ctx


class TopicListRedirectView(CatechismMixin, View):
    """Redirect old topic/chapter list to the unified grouped list."""

    def get(self, request, *args, **kwargs):
        return redirect(self.catechism.get_item_list_url())


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


class CompareListView(ListView):
    template_name = 'catechism/compare_list.html'
    model = ComparisonTheme
    context_object_name = 'themes'


class CompareThemeView(DetailView):
    template_name = 'catechism/compare_theme.html'
    model = ComparisonTheme
    slug_url_kwarg = 'theme_slug'
    context_object_name = 'theme'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        entries = self.object.entries.select_related('catechism').all()

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

        ctx['columns'] = columns

        # Prev/next theme navigation
        all_themes = list(ComparisonTheme.objects.all())
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
