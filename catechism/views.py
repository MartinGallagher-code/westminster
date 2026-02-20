from datetime import date

from django.db.models import Q, Prefetch
from django.views.generic import TemplateView, ListView, DetailView

from .models import Topic, Question, Commentary, FisherSubQuestion, ScripturePassage


class HomeView(TemplateView):
    template_name = 'catechism/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topics'] = Topic.objects.all()
        ctx['question_count'] = Question.objects.count()
        day_of_year = date.today().timetuple().tm_yday
        ctx['featured_question'] = Question.objects.filter(
            number=(day_of_year % 107) + 1
        ).first()
        return ctx


class QuestionListView(ListView):
    model = Question
    template_name = 'catechism/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        qs = Question.objects.select_related('topic')
        topic_slug = self.request.GET.get('topic')
        if topic_slug:
            qs = qs.filter(topic__slug=topic_slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topics'] = Topic.objects.all()
        ctx['active_topic'] = self.request.GET.get('topic', '')
        return ctx


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'catechism/question_detail.html'
    context_object_name = 'question'
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def get_queryset(self):
        return Question.objects.select_related('topic').prefetch_related(
            Prefetch(
                'commentaries',
                queryset=Commentary.objects.select_related('source').prefetch_related(
                    Prefetch(
                        'sub_questions',
                        queryset=FisherSubQuestion.objects.order_by('number')
                    )
                )
            )
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
            # Also look up continuation references (e.g., "15:4" from "Rev. 4:8; 15:4")
            # by checking references that weren't found directly
            found_refs = set(ctx['scripture_map'].keys())
            for ref in refs:
                if ref not in found_refs:
                    # Try matching by looking for passages whose reference matches
                    passage = ScripturePassage.objects.filter(reference=ref).first()
                    if passage:
                        ctx['scripture_map'][ref] = passage.text
        else:
            ctx['scripture_map'] = {}

        if self.request.user.is_authenticated:
            from accounts.models import UserNote
            from accounts.forms import NoteForm
            ctx['user_note'] = UserNote.objects.filter(
                user=self.request.user, question=q
            ).first()
            ctx['note_form'] = NoteForm()

        return ctx


class TopicListView(ListView):
    model = Topic
    template_name = 'catechism/topic_list.html'
    context_object_name = 'topics'


class TopicDetailView(DetailView):
    model = Topic
    template_name = 'catechism/topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['questions'] = Question.objects.filter(topic=self.object)
        return ctx


class SearchView(ListView):
    template_name = 'catechism/search_results.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Question.objects.none()

        return Question.objects.filter(
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query)
        ).distinct().select_related('topic')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx
