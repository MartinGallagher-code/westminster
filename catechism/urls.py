from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'catechism'

urlpatterns = [
    # Site-wide
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),

    # Scripture index
    path('scripture/', views.ScriptureIndexView.as_view(), name='scripture_index'),
    path('scripture/<slug:book_slug>/', views.ScriptureBookView.as_view(), name='scripture_book'),

    # Comparison view
    path('compare/', views.CompareListView.as_view(), name='compare_list'),
    path('compare/<slug:theme_slug>/', views.CompareThemeView.as_view(), name='compare_theme'),

    # Legacy WSC redirects (preserve old bookmarks)
    path('questions/', RedirectView.as_view(url='/wsc/questions/', permanent=True)),
    path('questions/<int:number>/', views.LegacyQuestionRedirect.as_view(), name='legacy_question'),
    path('topics/', RedirectView.as_view(url='/wsc/topics/', permanent=True)),
    path('topics/<slug:slug>/', views.LegacyTopicRedirect.as_view(), name='legacy_topic'),

    # Per-catechism routes
    path('<slug:catechism_slug>/', views.CatechismHomeView.as_view(), name='catechism_home'),
    path('<slug:catechism_slug>/questions/', views.QuestionListView.as_view(), name='question_list'),
    path('<slug:catechism_slug>/questions/<int:number>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('<slug:catechism_slug>/topics/', views.TopicListRedirectView.as_view(), name='topic_list'),
    path('<slug:catechism_slug>/topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),

    # Confession-specific routes (chapters & sections instead of topics & questions)
    path('<slug:catechism_slug>/sections/', views.QuestionListView.as_view(), name='section_list'),
    path('<slug:catechism_slug>/sections/<int:number>/', views.QuestionDetailView.as_view(), name='section_detail'),
    path('<slug:catechism_slug>/chapters/', views.TopicListRedirectView.as_view(), name='chapter_list'),
    path('<slug:catechism_slug>/chapters/<slug:slug>/', views.TopicDetailView.as_view(), name='chapter_detail'),
]
