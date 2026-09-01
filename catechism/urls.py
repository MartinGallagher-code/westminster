from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'catechism'

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # API
    path('api/question/<int:pk>/preview/', views.question_preview_json, name='question_preview'),
    path('api/suggest/', views.SearchSuggestView.as_view(), name='search_suggest'),

    # Site-wide
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('doctrine/', views.DoctrineIndexView.as_view(), name='doctrine_index'),
    path('doctrine/<slug:theme_slug>/', views.DoctrineDetailView.as_view(), name='doctrine_detail'),

    # Teaching guide (guided learning path)
    path('learn/', views.LearnIndexView.as_view(), name='learn_index'),
    path('learn/<slug:lesson_slug>/', views.LearnLessonView.as_view(), name='learn_lesson'),

    # Scripture index
    path('scripture/', views.ScriptureIndexView.as_view(), name='scripture_index'),
    path('scripture/<slug:book_slug>/', views.ScriptureBookView.as_view(), name='scripture_book'),

    # Comparison views
    path('compare/', views.CompareIndexView.as_view(), name='compare_index'),
    path('compare/custom/', views.CustomCompareView.as_view(), name='compare_custom'),
    path('compare/custom/<slug:theme_slug>/', views.CustomCompareThemeView.as_view(), name='compare_custom_theme'),
    path('compare/<slug:set_slug>/', views.CompareSetView.as_view(), name='compare_set'),
    path('compare/<slug:set_slug>/<slug:theme_slug>/', views.CompareSetThemeView.as_view(), name='compare_set_theme'),
    path('compare/<slug:set_slug>/<slug:theme_slug>/diff/',
         views.CompareDiffView.as_view(), name='compare_diff'),
    path('compare/<slug:set_slug>/<slug:theme_slug>/parallel/',
         views.ParallelReadView.as_view(), name='compare_parallel'),

    # Printable small-group handouts
    path('handout/<slug:catechism_slug>/<str:reference>/',
         views.HandoutView.as_view(), name='handout'),
    path('handout/<slug:catechism_slug>/topic/<slug:topic_slug>/',
         views.HandoutView.as_view(), name='handout_topic'),

    # Small-group tools
    path('present/<slug:catechism_slug>/', views.PresenterView.as_view(), name='presenter'),
    path('present/<slug:catechism_slug>/topic/<slug:topic_slug>/',
         views.PresenterView.as_view(), name='presenter_topic'),
    path('plan/', views.SessionPlanView.as_view(), name='session_plan'),

    # Citations: the reference a reader writes ("WCF 3.4"), made addressable
    path('cite/<slug:catechism_slug>/<str:reference>/',
         views.CitationPermalinkView.as_view(), name='citation_permalink'),
    path('cite/<slug:catechism_slug>/<str:reference>/<str:fmt>/',
         views.CitationExportView.as_view(), name='citation_export'),

    # Legacy WSC redirects (preserve old bookmarks)
    path('questions/', RedirectView.as_view(url='/wsc/questions/', permanent=True)),
    path('questions/<int:number>/', views.LegacyQuestionRedirect.as_view(), name='legacy_question'),
    path('topics/', RedirectView.as_view(url='/wsc/topics/', permanent=True)),
    path('topics/<slug:slug>/', views.LegacyTopicRedirect.as_view(), name='legacy_topic'),

    # Per-catechism routes
    path('<slug:catechism_slug>/', views.CatechismHomeView.as_view(), name='catechism_home'),
    path('<slug:catechism_slug>/questions/', views.TopicListRedirectView.as_view(), name='question_list'),
    path('<slug:catechism_slug>/questions/<int:number>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('<slug:catechism_slug>/topics/', views.TopicListRedirectView.as_view(), name='topic_list'),
    path('<slug:catechism_slug>/topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),

    # Confession-specific routes (chapters & sections instead of topics & questions)
    path('<slug:catechism_slug>/sections/', views.TopicListRedirectView.as_view(), name='section_list'),
    path('<slug:catechism_slug>/sections/<int:number>/', views.QuestionDetailView.as_view(), name='section_detail'),
    path('<slug:catechism_slug>/chapters/', views.TopicListRedirectView.as_view(), name='chapter_list'),
    path('<slug:catechism_slug>/chapters/<slug:slug>/', views.TopicDetailView.as_view(), name='chapter_detail'),
]
