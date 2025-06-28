# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('list/', views.ReportListView.as_view(), name='report_list'),
    path('export/csv/', views.ReportExportCSV.as_view(), name='report_export_csv'),
]
