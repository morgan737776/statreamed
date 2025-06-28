from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views
from .views_theme import toggle_theme
from .views import HomeView, contact_view, about_view, PortalHomeView
from .views_calendar import CalendarView, get_appointments, create_appointment, update_appointment, delete_appointment
from .views_security import security_dashboard, security_api_stats, export_audit_logs
from .api_views import get_patients, get_doctors, get_services
from .api import router as api_router
from .api_statistics import StatisticsView

app_name = 'core'

# Admin URLs (using custom admin site)
admin_urls = [
    path('admin_panel/', include('core.urls_admin', namespace='admin_panel')),
]

# Main site URLs
schema_view = get_schema_view(
    openapi.Info(
        title="Medical Center API",
        default_version='v1',
        description="API для интеграции с внешними медицинскими системами",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', PortalHomeView.as_view(), name='home'),
    path('api/', include(api_router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/statistics/', StatisticsView.as_view(), name='api_statistics'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('home-old/', HomeView.as_view(), name='home_old'),
    path('about/', about_view, name='about'),
    path('statistics/', TemplateView.as_view(template_name='core/statistics.html'), name='statistics'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('contact/', contact_view, name='contact'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('terms-of-service/', TemplateView.as_view(template_name='terms_of_service.html'), name='terms_of_service'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        redirect_authenticated_user=True,
        next_page='core:dashboard'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/auth/password_reset_form.html',
        email_template_name='core/auth/password_reset_email.html',
        subject_template_name='core/auth/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/auth/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('admin-panel/', include(admin_urls)),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_add'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('calendar/', TemplateView.as_view(template_name='core/calendar.html'), name='calendar'),
    path('api/appointments/', views.get_all_appointments, name='api_all_appointments'),
    path('appointments/create/', views.create_appointment_view, name='create_appointment'),
    path('programs/', TemplateView.as_view(template_name='core/programs.html'), name='programs'),
    path('reports/', include([
        path('', views.ReportsHomeView.as_view(), name='reports_home'),
        path('patients/', views.report_patient_statistics, name='report_patients'),
        path('beds/', views.report_beds, name='report_beds'),
        path('finance/', views.report_finance, name='report_finance'),
        path('staff/', views.report_staff, name='report_staff'),
        path('appointments/', views.report_appointments, name='report_appointments'),
        path('rehab/', views.report_rehab, name='report_rehab'),
    ])),
    path('documents/', TemplateView.as_view(template_name='core/documents.html'), name='documents'),
    path('staff/', include('core.urls_staff')),
    path('settings/', views.settings_hub, name='settings'),
    path('create_user/', views.create_user, name='create_user'),
    path('edit_user/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:pk>/', views.delete_user, name='delete_user'),
    path('change_user_role/<int:pk>/', views.change_user_role, name='change_user_role'),
    path('set_theme/', views.set_theme, name='set_theme'),
    path('export_patients/', views.export_patients, name='export_patients'),
    path('import_patients/', views.import_patients, name='import_patients'),
    path('export_admissions/', views.export_admissions, name='export_admissions'),
    path('import_admissions/', views.import_admissions, name='import_admissions'),
    path('django-admin/', admin.site.urls),
    path('api/dashboard-stats/', views.get_dashboard_stats, name='api_dashboard_stats'),
    path('api/all-appointments/', views.get_all_appointments, name='api_all_appointments'),
    path('api/calendar/appointments/<int:appointment_id>/delete/', delete_appointment, name='delete_appointment'),
    path('api/patients/', get_patients, name='api_patients'),
    path('api/doctors/', get_doctors, name='api_doctors'),
    path('api/services/', get_services, name='api_services'),
    path('theme/toggle/', require_POST(toggle_theme), name='theme_toggle'),
    path('security/', security_dashboard, name='security_dashboard'),
    path('security/api-stats/', security_api_stats, name='security_api_stats'),
    path('security/export-audit-logs/', export_audit_logs, name='export_audit_logs'),
]
