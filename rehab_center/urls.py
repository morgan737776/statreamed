"""
URL configuration for rehab_center project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from commissions.admin_site import admin_site as commissions_admin_site
from .sitemap import get_sitemaps

# Use our custom admin site
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('admin-panel/', include('core.urls', namespace='admin_panel')),

    # App URLs
    path('programs/', include('rehab_programs.urls', namespace='rehab_programs')),
    path('patients/', include('rehabilitation.urls', namespace='rehabilitation')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('portal/', include('patient_portal.urls', namespace='patient_portal')),
    path('commissions/', include('commissions.urls', namespace='commissions')),
    path('emr/', include('emr.urls', namespace='emr')),
    path('medical/', include('medical_history.urls')),
    path('inpatient/', include('inpatient.urls', namespace='inpatient')),
    path('services/', include('services.urls', namespace='services')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('select2/', include('django_select2.urls')),

    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),
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

    # SEO URLs
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': get_sitemaps(None)}, name='django.contrib.sitemaps.views.sitemap'),

    # Core URL (should be last)
    path('', include('core.urls')),
]

# Serve static and media files during development
# Serve static and media files in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar and performance settings
if settings.DEBUG:
    import debug_toolbar
    import mimetypes
    
    # Add support for static files debugging
    mimetypes.add_type("application/javascript", ".js", True)
    
    # Configure debug toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'SHOW_TEMPLATE_CONTEXT': True,
        'SQL_WARNING_THRESHOLD': 100,  # milliseconds
    }
    
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
