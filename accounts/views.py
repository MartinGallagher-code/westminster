import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, View
from django.http import HttpResponseRedirect, JsonResponse

from .models import UserNote, Highlight
from .forms import NoteForm, SignupForm
from catechism.models import Question, Commentary


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')


class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'accounts/dashboard.html'
    context_object_name = 'notes'

    def get_queryset(self):
        return UserNote.objects.filter(
            user=self.request.user
        ).select_related('question', 'question__topic', 'question__catechism').order_by('question__number')


class NoteSaveView(LoginRequiredMixin, View):
    """Create or update a note for a question (one note per user per question)."""

    def post(self, request, question_pk):
        question = get_object_or_404(Question, pk=question_pk)
        text = request.POST.get('text', '').strip()

        if text:
            UserNote.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'text': text}
            )

        return HttpResponseRedirect(question.get_absolute_url())


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = UserNote
    template_name = 'accounts/note_confirm_delete.html'

    def get_queryset(self):
        return UserNote.objects.filter(user=self.request.user)

    def get_success_url(self):
        return self.object.question.get_absolute_url()


class HighlightListCreateView(LoginRequiredMixin, View):
    def get(self, request):
        commentary_ids = request.GET.getlist('commentary_id')
        highlights = Highlight.objects.filter(
            user=request.user,
            commentary_id__in=commentary_ids
        ).values('id', 'commentary_id', 'selected_text', 'occurrence_index')
        return JsonResponse({'highlights': list(highlights)})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        commentary_id = data.get('commentary_id')
        selected_text = data.get('selected_text', '').strip()
        occurrence_index = data.get('occurrence_index', 0)

        if not commentary_id or not selected_text:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        commentary = get_object_or_404(Commentary, pk=commentary_id)

        highlight, created = Highlight.objects.get_or_create(
            user=request.user,
            commentary=commentary,
            selected_text=selected_text,
            occurrence_index=occurrence_index,
        )
        return JsonResponse({
            'id': highlight.id,
            'created': created,
        }, status=201 if created else 200)


class HighlightDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        deleted, _ = Highlight.objects.filter(
            pk=pk, user=request.user
        ).delete()
        if deleted:
            return JsonResponse({'deleted': True})
        return JsonResponse({'error': 'Not found'}, status=404)
