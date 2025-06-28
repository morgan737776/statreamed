# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'patient_portal'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
