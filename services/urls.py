from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views_dashboard import ServicesDashboardView

app_name = 'services'

from django.views.generic import TemplateView

urlpatterns = [
    # Service Categories
    path('categories/', views.ServiceCategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.ServiceCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/', views.ServiceCategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/edit/', views.ServiceCategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.ServiceCategoryDeleteView.as_view(), name='category_delete'),
    
    # Service Items
    path('services/', views.ServiceItemListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceItemCreateView.as_view(), name='service_add'),
    path('services/<int:pk>/', views.ServiceItemDetailView.as_view(), name='service_detail'),
    path('services/<int:pk>/edit/', views.ServiceItemUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceItemDeleteView.as_view(), name='service_delete'),
    
    # Service Appointments
    path('appointments/', views.ServiceAppointmentListView.as_view(), name='appointment_list'),
    path('appointments/calendar/', views.ServiceAppointmentCalendarView.as_view(), name='appointment_calendar'),
    path('appointments/add/', views.ServiceAppointmentCreateView.as_view(), name='appointment_add'),
    path('appointments/<int:pk>/', views.ServiceAppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.ServiceAppointmentUpdateView.as_view(), name='appointment_edit'),
    path('appointments/<int:pk>/cancel/', views.ServiceAppointmentCancelView.as_view(), name='appointment_cancel'),
    
    # Service Contracts
    path('contracts/', views.ServiceContractListView.as_view(), name='contract_list'),
    path('contracts/add/', views.ServiceContractCreateView.as_view(), name='contract_add'),
    path('contracts/<int:pk>/', views.ServiceContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.ServiceContractUpdateView.as_view(), name='contract_edit'),
    path('contracts/<int:pk>/print/', views.ServiceContractPrintView.as_view(), name='contract_print'),
    path('contracts/<int:pk>/email/', views.ServiceContractEmailView.as_view(), name='contract_email'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/receipt/', views.PaymentReceiptView.as_view(), name='payment_receipt'),
    path('payments/<int:pk>/email/', views.PaymentEmailView.as_view(), name='payment_email'),
    
    # Dashboard
    path('dashboard/', ServicesDashboardView.as_view(), name='dashboard'),

    # API Endpoints
    path('api/services-by-category/', views.services_by_category, name='api_services_by_category'),
    path('api/available-slots/', views.get_available_slots, name='api_available_slots'),
    path('api/calculate-price/', views.calculate_service_price, name='api_calculate_price'),
    path('api/contract-pdf/<int:pk>/', views.generate_contract_pdf, name='api_contract_pdf'),

    # Reports
    path('reports/', TemplateView.as_view(template_name='services/reports/report_list.html'), name='report_list'),
    path('reports/services/', views.ServiceReportView.as_view(), name='report_services'),
    path('reports/payments/', views.PaymentReportView.as_view(), name='report_payments'),
    path('reports/contracts/', views.ContractReportView.as_view(), name='report_contracts'),
]
