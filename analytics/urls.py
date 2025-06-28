# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'analytics'

# URL patterns for the analytics app
urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('program-effectiveness/', views.program_effectiveness_report, name='program_effectiveness_report'),
    path('specialist-workload/', views.specialist_workload_report, name='specialist_workload_report'),
    path('program-intensity/', views.program_intensity_report, name='program_intensity_report'),
]
