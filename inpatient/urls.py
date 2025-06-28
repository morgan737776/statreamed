# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'inpatient'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('hospitalize/', views.hospitalize_patient, name='hospitalize_patient'),
    path('bed/<int:bed_id>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('admission-request/add/', views.add_admission_request, name='add_admission_request'),
    path('gantt/', views.gantt_chart_view, name='gantt_chart'),
    path('api/gantt-data/', views.gantt_data_api, name='gantt_data_api'),
]
