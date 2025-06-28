# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'rehab_programs'

urlpatterns = [
    path('', views.RehabilitationProgramListView.as_view(), name='rehab_program_list'),
    path('create/', views.RehabilitationProgramCreateView.as_view(), name='rehab_program_create'),
    path('<int:pk>/edit/', views.RehabilitationProgramUpdateView.as_view(), name='rehab_program_edit'),
    path('<int:pk>/delete/', views.RehabilitationProgramDeleteView.as_view(), name='rehab_program_delete'),

    path('activity/create/', views.ScheduledActivityCreateView.as_view(), name='scheduled_activity_create'),
    path('activity/<int:pk>/edit/', views.ScheduledActivityUpdateView.as_view(), name='scheduled_activity_edit'),
    path('activity/<int:pk>/delete/', views.ScheduledActivityDeleteView.as_view(), name='scheduled_activity_delete'),

    path('patient/<int:patient_pk>/add_program/', views.add_rehab_program, name='add_rehab_program'),
    path('<int:program_pk>/', views.rehab_program_detail, name='rehab_program_detail'),
    path('<int:program_pk>/add_activity/', views.add_scheduled_activity, name='add_scheduled_activity'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar-events/', views.calendar_api, name='calendar_api'),
]
