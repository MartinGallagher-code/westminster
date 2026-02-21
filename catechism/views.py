from datetime import date

from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .models import Catechism, Topic, Question, Commentary, FisherSubQuestion, ScripturePassage, CrossReference


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
            ).first()
            cat.topics_list = Topic.objects.filter(catechism=cat)
        ctx['catechisms'] = catechisms
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
        ).first()
        return ctx


class QuestionListView(CatechismMixin, ListView):
    template_name = 'catechism/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        qs = Question.objects.filter(catechism=self.catechism).select_related('topic')
        topic_slug = self.request.GET.get('topic')
        if topic_slug:
            qs = qs.filter(topic__slug=topic_slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topics'] = Topic.objects.filter(catechism=self.catechism)
        ctx['active_topic'] = self.request.GET.get('topic', '')
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

        # For confessions, compute the section number within the chapter
        if self.catechism.is_confession and q.topic:
            ctx['section_number'] = q.number - q.topic.question_start + 1

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

        # Cross-references between WSC and WLC
        if self.catechism.slug == 'wsc':
            cross_refs = CrossReference.objects.filter(
                wsc_question=q
            ).select_related('wlc_question')
            ctx['cross_refs'] = [cr.wlc_question for cr in cross_refs]
            ctx['cross_ref_label'] = 'WLC'
        elif self.catechism.slug == 'wlc':
            cross_refs = CrossReference.objects.filter(
                wlc_question=q
            ).select_related('wsc_question')
            ctx['cross_refs'] = [cr.wsc_question for cr in cross_refs]
            ctx['cross_ref_label'] = 'WSC'

        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            from accounts.forms import NoteForm
            ctx['user_note'] = UserNote.objects.filter(
                user=self.request.user, question=q
            ).first()
            ctx['note_form'] = NoteForm()

        return ctx


class TopicListView(CatechismMixin, ListView):
    template_name = 'catechism/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter(catechism=self.catechism)


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


# Legacy redirects
class LegacyQuestionRedirect(View):
    def get(self, request, number):
        return redirect('catechism:question_detail',
                        catechism_slug='wsc', number=number, permanent=True)


class LegacyTopicRedirect(View):
    def get(self, request, slug):
        return redirect('catechism:topic_detail',
                        catechism_slug='wsc', slug=slug, permanent=True)
