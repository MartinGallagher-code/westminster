import json
import logging
from datetime import datetime, timezone

import bleach
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, DeleteView, View
from django.http import HttpResponseRedirect, JsonResponse
from django_ratelimit.decorators import ratelimit

from .models import UserNote, Highlight, InlineComment, SupporterSubscription, UserProfile
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


# --- Supporter subscription views ---


class SupportPageView(LoginRequiredMixin, View):
    """Display the support page with subscription status and checkout button."""

    def get(self, request):
        subscription = SupporterSubscription.objects.filter(
            user=request.user
        ).first()
        return render(request, 'accounts/support.html', {
            'subscription': subscription,
        })


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    """Create a Stripe Checkout session and redirect the user to it."""

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        subscription = SupporterSubscription.objects.filter(
            user=request.user
        ).first()

        if subscription and subscription.is_active:
            messages.info(request, 'You already have an active subscription.')
            return HttpResponseRedirect(reverse_lazy('accounts:support'))

        if subscription and subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={'django_user_id': str(request.user.pk)},
            )
            customer_id = customer.id
            SupporterSubscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'stripe_customer_id': customer_id,
                    'status': 'incomplete',
                }
            )

        domain = request.build_absolute_uri('/')[:-1]

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=domain + '/accounts/support/success/'
            '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain + '/accounts/support/cancel/',
            metadata={'django_user_id': str(request.user.pk)},
        )

        return HttpResponseRedirect(checkout_session.url)


class CheckoutSuccessView(LoginRequiredMixin, View):
    """Display a thank-you page after successful checkout."""

    def get(self, request):
        return render(request, 'accounts/support_success.html')


class CheckoutCancelView(LoginRequiredMixin, View):
    """Display a page when the user cancels checkout."""

    def get(self, request):
        messages.info(
            request,
            'Checkout was cancelled. You can subscribe any time.'
        )
        return HttpResponseRedirect(reverse_lazy('accounts:support'))


class CustomerPortalView(LoginRequiredMixin, View):
    """Redirect authenticated user to the Stripe Customer Portal."""

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = SupporterSubscription.objects.filter(
            user=request.user
        ).first()

        if not subscription or not subscription.stripe_customer_id:
            messages.error(request, 'No subscription found.')
            return HttpResponseRedirect(reverse_lazy('accounts:support'))

        domain = request.build_absolute_uri('/')[:-1]
        portal_session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=domain + '/accounts/dashboard/',
        )
        return HttpResponseRedirect(portal_session.url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events for subscription lifecycle."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.warning('Stripe webhook: invalid payload')
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning('Stripe webhook: invalid signature')
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    event_type = event['type']
    data_object = event['data']['object']

    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(data_object)
    elif event_type == 'customer.subscription.updated':
        _handle_subscription_updated(data_object)
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_deleted(data_object)
    elif event_type == 'invoice.payment_failed':
        _handle_payment_failed(data_object)
    else:
        logger.info('Stripe webhook: unhandled event type %s', event_type)

    return JsonResponse({'status': 'ok'})


def _handle_checkout_completed(session):
    """Checkout completed -- link subscription to user."""
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')

    if not customer_id or not subscription_id:
        return

    try:
        sub = SupporterSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_sub = stripe.Subscription.retrieve(subscription_id)

        sub.stripe_subscription_id = subscription_id
        sub.status = stripe_sub.status
        sub.current_period_end = datetime.fromtimestamp(
            stripe_sub.current_period_end, tz=timezone.utc
        )
        sub.save()
    except SupporterSubscription.DoesNotExist:
        logger.warning(
            'Stripe webhook: no SupporterSubscription for customer %s',
            customer_id
        )


def _handle_subscription_updated(subscription):
    """Subscription status changed (e.g., renewed, past_due)."""
    subscription_id = subscription.get('id')
    try:
        sub = SupporterSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        sub.status = subscription.get('status', sub.status)
        period_end = subscription.get('current_period_end')
        if period_end:
            sub.current_period_end = datetime.fromtimestamp(
                period_end, tz=timezone.utc
            )
        sub.save()
    except SupporterSubscription.DoesNotExist:
        logger.warning(
            'Stripe webhook: no SupporterSubscription for subscription %s',
            subscription_id
        )


def _handle_subscription_deleted(subscription):
    """Subscription canceled/ended."""
    subscription_id = subscription.get('id')
    try:
        sub = SupporterSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        sub.status = 'canceled'
        sub.save()
    except SupporterSubscription.DoesNotExist:
        logger.warning(
            'Stripe webhook: no SupporterSubscription for subscription %s',
            subscription_id
        )


def _handle_payment_failed(invoice):
    """Mark subscription as past_due when payment fails."""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return
    try:
        sub = SupporterSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        sub.status = 'past_due'
        sub.save()
    except SupporterSubscription.DoesNotExist:
        logger.warning(
            'Stripe webhook: no SupporterSubscription for subscription %s',
            subscription_id
        )


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

        subscription = SupporterSubscription.objects.filter(user=target_user).first()

        return render(request, 'accounts/admin_user_detail.html', {
            'target_user': target_user,
            'notes': notes,
            'highlights': highlights,
            'comments': comments,
            'subscription': subscription,
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
