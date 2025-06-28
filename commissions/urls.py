from django.urls import path
from . import views

app_name = 'commissions'

urlpatterns = [
    path('', views.CommissionDashboardView.as_view(), name='dashboard'),
    path('application/add/', views.ApplicationCreateView.as_view(), name='application_add'),
    path('application/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('application/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('application/<int:app_pk>/conclusion/add/', views.MedicalCommitteeConclusionCreateView.as_view(), name='conclusion_add'),
    path('conclusion/<int:pk>/update/', views.MedicalCommitteeConclusionUpdateView.as_view(), name='conclusion_update'),

    # Календарь
    path('calendar/', views.CommissionCalendarView.as_view(), name='calendar'),
    path('api/events/', views.commission_events_api, name='events_api'),
]
