from django.urls import path
from django.contrib.auth import views as auth_views
from django_ratelimit.decorators import ratelimit
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', ratelimit(key='ip', rate='10/m', method='POST', block=True)(
        auth_views.LoginView.as_view(template_name='accounts/login.html')
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('notes/save/<int:question_pk>/', views.NoteSaveView.as_view(), name='note_save'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    path('highlights/', views.HighlightListCreateView.as_view(), name='highlight_list_create'),
    path('highlights/<int:pk>/delete/', views.HighlightDeleteView.as_view(), name='highlight_delete'),

    path('comments/', views.InlineCommentListCreateView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/update/', views.InlineCommentUpdateView.as_view(), name='comment_update'),
    path('comments/<int:pk>/delete/', views.InlineCommentDeleteView.as_view(), name='comment_delete'),

    # Password change
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),

    # Supporter subscription
    path('support/', views.SupportPageView.as_view(), name='support'),
    path('support/checkout/', views.CreateCheckoutSessionView.as_view(), name='support_checkout'),
    path('support/success/', views.CheckoutSuccessView.as_view(), name='support_success'),
    path('support/cancel/', views.CheckoutCancelView.as_view(), name='support_cancel'),
    path('support/portal/', views.CustomerPortalView.as_view(), name='support_portal'),
    path('support/webhook/', views.stripe_webhook, name='stripe_webhook'),

    # Admin panel
    path('manage/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('manage/users/<int:user_id>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('manage/users/<int:user_id>/block/', views.AdminUserBlockView.as_view(), name='admin_user_block'),
    path('manage/users/<int:user_id>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
]
