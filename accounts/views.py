import json

import bleach
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DeleteView, View
from django.http import HttpResponseRedirect, JsonResponse
from django_ratelimit.decorators import ratelimit

from .models import UserNote, Highlight, InlineComment
from .forms import SignupForm
from catechism.models import Question, Commentary


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
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
        ).select_related(
            'question', 'question__topic', 'question__catechism'
        ).order_by('question__catechism__name', 'question__number')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inline_comments'] = InlineComment.objects.filter(
            user=self.request.user
        ).select_related(
            'question', 'question__topic', 'question__catechism',
            'commentary__source'
        ).order_by('-updated_at')[:50]
        return ctx


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


@method_decorator(ratelimit(key='user', rate='60/m', method='POST', block=True), name='post')
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
        selected_text = bleach.clean(data.get('selected_text', '').strip())
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


@method_decorator(ratelimit(key='user', rate='60/m', method='POST', block=True), name='post')
class InlineCommentListCreateView(LoginRequiredMixin, View):
    def get(self, request):
        question_id = request.GET.get('question_id')
        if not question_id:
            return JsonResponse({'error': 'question_id required'}, status=400)

        comments = InlineComment.objects.filter(
            user=request.user,
            question_id=question_id
        ).values(
            'id', 'content_type_tag', 'commentary_id',
            'selected_text', 'occurrence_index',
            'comment_text', 'created_at', 'updated_at'
        )
        return JsonResponse({'comments': list(comments)})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        question_id = data.get('question_id')
        content_type_tag = data.get('content_type_tag')
        commentary_id = data.get('commentary_id')
        selected_text = bleach.clean(data.get('selected_text', '').strip())
        occurrence_index = data.get('occurrence_index', 0)
        comment_text = bleach.clean(data.get('comment_text', '').strip())

        if not question_id or not selected_text or not comment_text or not content_type_tag:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if content_type_tag not in ('question', 'answer', 'commentary'):
            return JsonResponse({'error': 'Invalid content_type_tag'}, status=400)

        question = get_object_or_404(Question, pk=question_id)
        commentary = get_object_or_404(Commentary, pk=commentary_id) if commentary_id else None

        comment = InlineComment.objects.create(
            user=request.user,
            question=question,
            commentary=commentary,
            content_type_tag=content_type_tag,
            selected_text=selected_text,
            occurrence_index=occurrence_index,
            comment_text=comment_text,
        )
        return JsonResponse({
            'id': comment.id,
            'created_at': comment.created_at.isoformat(),
        }, status=201)


class InlineCommentUpdateView(LoginRequiredMixin, View):
    def patch(self, request, pk):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        comment_text = bleach.clean(data.get('comment_text', '').strip())
        if not comment_text:
            return JsonResponse({'error': 'comment_text required'}, status=400)

        updated = InlineComment.objects.filter(
            pk=pk, user=request.user
        ).update(comment_text=comment_text)
        if updated:
            return JsonResponse({'updated': True})
        return JsonResponse({'error': 'Not found'}, status=404)


class InlineCommentDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        deleted, _ = InlineComment.objects.filter(
            pk=pk, user=request.user
        ).delete()
        if deleted:
            return JsonResponse({'deleted': True})
        return JsonResponse({'error': 'Not found'}, status=404)
