from django.urls import path
from . import views


app_name = 'westminster_standards'


urlpatterns = [
    path('', views.home, name='home'),
    path('ontology/', views.ontology, name='ontology'),
    path('personas/', views.personas_list, name='personas_list'),
    path('personas/<slug:slug>/', views.persona_detail, name='persona_detail'),
    path('compare/', views.compare_personas, name='compare_personas'),
    path('compare-schools/', views.compare_schools, name='compare_schools'),
    path('dimensions/', views.dimension_pairs, name='dimension_pairs'),
    path('dimensions/<slug:pair_key>/', views.dimension_pair_detail, name='dimension_pair_detail'),
    path('cruxes/', views.cruxes_list, name='cruxes_list'),
    path('cruxes/<slug:slug>/', views.crux_detail, name='crux_detail'),
    path('schools/', views.schools_list, name='schools_list'),
    path('schools/<slug:slug>/', views.school_detail, name='school_detail'),
    path('works/', views.works_list, name='works_list'),
    path('works/wcf/chapter/<int:number>/', views.wcf_chapter_detail, name='wcf_chapter'),
    path('works/<slug:catechism_slug>/q/<int:number>/',
         views.catechism_question_detail, name='catechism_question'),
    path('works/<slug:slug>/', views.work_detail, name='work_detail'),
    path('dimension/<slug:dim_key>/', views.dimension_detail, name='dimension_detail'),
    path('dimension/<slug:dim_key>/<slug:attr_key>/<slug:value_key>/',
         views.value_detail, name='value_detail'),
    path('heads/', views.heads_list, name='heads_list'),
    path('heads/<slug:slug>/', views.head_detail, name='head_detail'),
    path('search/', views.search, name='search'),
]
