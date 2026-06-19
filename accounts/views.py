import json
import logging

import bleach
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DeleteView, TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse
from django_ratelimit.decorators import ratelimit

from .models import UserNote, Highlight, InlineComment, UserProfile
from .forms import SignupForm
from catechism.models import Question, Commentary

logger = logging.getLogger(__name__)


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
        ctx['recent_notes'] = UserNote.objects.filter(
            user=self.request.user
        ).select_related(
            'question', 'question__topic', 'question__catechism'
        ).order_by('-updated_at')[:5]
        ctx['note_count'] = UserNote.objects.filter(user=self.request.user).count()
        ctx['annotation_count'] = InlineComment.objects.filter(user=self.request.user).count()
        ctx['highlight_count'] = Highlight.objects.filter(user=self.request.user).count()
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

        question = get_object_or_404(Question, pk=question_id)

        # Direct annotations for this question
        own_filter = Q(user=request.user, question_id=question_id)

        # Also include commentary annotations from sibling commentaries
        # that share identical body text (e.g. WLC fifth-commandment questions).
        local_commentaries = {c.source_id: c for c in question.commentaries.all()}
        sibling_map = {}  # sibling_commentary_id -> local_commentary_id
        for c in local_commentaries.values():
            if c.body:
                sibling_ids = Commentary.objects.filter(
                    source=c.source, body=c.body
                ).exclude(pk=c.pk).values_list('id', flat=True)
                for sid in sibling_ids:
                    sibling_map[sid] = c.id

        sibling_filter = Q()
        if sibling_map:
            sibling_filter = Q(
                user=request.user,
                content_type_tag='commentary',
                commentary_id__in=list(sibling_map.keys()),
            )

        comments = list(
            InlineComment.objects.filter(own_filter | sibling_filter)
            .values(
                'id', 'content_type_tag', 'commentary_id',
                'selected_text', 'occurrence_index',
                'comment_text', 'created_at', 'updated_at'
            )
            .distinct()
        )

        # Remap sibling commentary_ids to the local commentary for this question
        for comment in comments:
            cid = comment.get('commentary_id')
            if cid and cid in sibling_map:
                comment['commentary_id'] = sibling_map[cid]

        return JsonResponse({'comments': comments})

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

        valid_tags = [t[0] for t in InlineComment.CONTENT_TYPE_CHOICES]
        if content_type_tag not in valid_tags:
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


# --- Support view ---


class SupportPageView(TemplateView):
    """Display the support page linking out to Buy Me a Coffee."""

    template_name = 'accounts/support.html'


# --- Admin panel views ---


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only allow staff/superusers access."""

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AdminUserListView(AdminRequiredMixin, View):
    """List all users with usage stats."""

    def get(self, request):
        users = User.objects.annotate(
            note_count=Count('notes', distinct=True),
            highlight_count=Count('highlights', distinct=True),
            comment_count=Count('inline_comments', distinct=True),
        ).select_related('profile').order_by('-date_joined')

        return render(request, 'accounts/admin_user_list.html', {
            'users': users,
        })


class AdminUserDetailView(AdminRequiredMixin, View):
    """Show detailed info for a single user."""

    def get(self, request, user_id):
        target_user = get_object_or_404(
            User.objects.select_related('profile'),
            pk=user_id,
        )
        notes = UserNote.objects.filter(user=target_user).select_related(
            'question', 'question__catechism'
        ).order_by('-updated_at')[:20]
        highlights = Highlight.objects.filter(user=target_user).order_by('-created_at')[:20]
        comments = InlineComment.objects.filter(user=target_user).select_related(
            'question', 'question__catechism'
        ).order_by('-updated_at')[:20]

        return render(request, 'accounts/admin_user_detail.html', {
            'target_user': target_user,
            'notes': notes,
            'highlights': highlights,
            'comments': comments,
            'note_count': UserNote.objects.filter(user=target_user).count(),
            'highlight_count': Highlight.objects.filter(user=target_user).count(),
            'comment_count': InlineComment.objects.filter(user=target_user).count(),
        })


class AdminUserBlockView(AdminRequiredMixin, View):
    """Toggle block/unblock for a user."""

    def post(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'You cannot block yourself.')
            return redirect('accounts:admin_user_list')

        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.is_blocked = not profile.is_blocked
        profile.save()

        action = 'blocked' if profile.is_blocked else 'unblocked'
        messages.success(request, f'User "{target_user.username}" has been {action}.')
        return redirect('accounts:admin_user_detail', user_id=user_id)


class AdminUserDeleteView(AdminRequiredMixin, View):
    """Delete a user account."""

    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'You cannot delete yourself.')
            return redirect('accounts:admin_user_list')
        return render(request, 'accounts/admin_user_delete.html', {
            'target_user': target_user,
        })

    def post(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'You cannot delete yourself.')
            return redirect('accounts:admin_user_list')

        username = target_user.username
        target_user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
        return redirect('accounts:admin_user_list')


# --- Password change view ---


class PasswordChangeView(LoginRequiredMixin, View):
    """Allow users to change their own password."""

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'accounts/password_change.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed.')
            return redirect('accounts:dashboard')
        return render(request, 'accounts/password_change.html', {'form': form})
