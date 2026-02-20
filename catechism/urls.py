from django.urls import path
from . import views

app_name = 'catechism'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:number>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('topics/', views.TopicListView.as_view(), name='topic_list'),
    path('topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
]
