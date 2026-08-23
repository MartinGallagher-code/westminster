from django.urls import path, reverse_lazy
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

    # Password reset sends mail and confirms whether an address is registered,
    # so it is throttled like the other credential endpoints.
    # success_url must be namespaced: Django's default reverses the bare name
    # 'password_reset_done', which does not exist under the accounts namespace,
    # so submitting the form raised NoReverseMatch.
    path('password-reset/', ratelimit(key='ip', rate='5/m', method='POST', block=True)(
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            success_url=reverse_lazy('accounts:password_reset_done'),
        )
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('notes/save/<int:question_pk>/', views.NoteSaveView.as_view(), name='note_save'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    path('highlights/', views.HighlightListCreateView.as_view(), name='highlight_list_create'),
    path('highlights/<int:pk>/delete/', views.HighlightDeleteView.as_view(), name='highlight_delete'),

    path('comments/', views.InlineCommentListCreateView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/update/', views.InlineCommentUpdateView.as_view(), name='comment_update'),
    path('comments/<int:pk>/delete/', views.InlineCommentDeleteView.as_view(), name='comment_delete'),

    path('notes/export/', views.NotesExportView.as_view(), name='notes_export'),

    # Memorisation
    path('memorize/', views.MemorizeHomeView.as_view(), name='memorize'),
    path('memorize/review/', views.MemorizeReviewView.as_view(), name='memorize_review'),
    path('memorize/add/<int:question_pk>/', views.MemorizeAddView.as_view(), name='memorize_add'),
    path('memorize/remove/<int:question_pk>/', views.MemorizeRemoveView.as_view(), name='memorize_remove'),
    path('memorize/add-document/', views.MemorizeAddDocumentView.as_view(), name='memorize_add_document'),

    # Password change
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),

    # Support the project
    path('support/', views.SupportPageView.as_view(), name='support'),

    # Admin panel
    path('manage/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('manage/users/<int:user_id>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('manage/users/<int:user_id>/block/', views.AdminUserBlockView.as_view(), name='admin_user_block'),
    path('manage/users/<int:user_id>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
]
