from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, F, Sum, Case, When, Value, IntegerField
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.db.models import F, Q, Count, Case, When, Value, IntegerField
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Patient

from .models import SystemSettings, IntegrationSettings, AuditLog, Staff, Appointment, Notification, TreatmentReminder, ExternalCalendarSync, MedicalRecord
from .forms import PatientSearchForm

User = get_user_model()

def staff_required(view_func):
    """Decorator for views that checks that the user is a staff member."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'У вас нет прав доступа к этой странице.')
            return redirect('admin_panel:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@staff_required
def admin_dashboard(request):
    """Admin dashboard view with statistics and overview."""
    total_patients = Patient.objects.count()
    total_staff = Staff.objects.count() if 'Staff' in [model.__name__ for model in Patient._meta.apps.get_models()] else 0
    
    # Appointment statistics
    from datetime import date
    today = date.today()
    today_appointments = Appointment.objects.filter(date=today).count()
    
    # Notification statistics
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # Recent patients
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient').order_by('-created_at')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_staff': total_staff,
        'today_appointments': today_appointments,
        'unread_notifications': unread_notifications,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def integration_1c_medicine_view(request):
    """
    Отображает страницу для управления настройками интеграции с 1С:Медицина.
    Позволяет просматривать, добавлять и редактировать параметры подключения.
    """
    integration_settings, created = Integration1C.objects.get_or_create(id=1)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_settings':
            integration_settings.name = request.POST.get('name', integration_settings.name)
            integration_settings.api_url = request.POST.get('api_url', integration_settings.api_url)
            integration_settings.login = request.POST.get('login', integration_settings.login)
            integration_settings.is_active = 'is_active' in request.POST
            password = request.POST.get('password')
            if password:
                integration_settings.password = password
            integration_settings.save()
            messages.success(request, 'Настройки успешно сохранены.')

        elif action in ['sync_patients', 'sync_appointments']:
            try:
                service = Integration1CService()
                if action == 'sync_patients':
                    result = service.sync_patients()
                else:
                    result = service.sync_appointments()
                
                integration_settings.last_sync_time = timezone.now()
                integration_settings.last_sync_status = 'Успешно' if result.get('status') == 'success' else 'Ошибка'
                integration_settings.last_sync_details = str(result)
                messages.success(request, f'Синхронизация ({action}) завершена.')

            except Exception as e:
                integration_settings.last_sync_time = timezone.now()
                integration_settings.last_sync_status = 'Критическая ошибка'
                integration_settings.last_sync_details = str(e)
                messages.error(request, f'Ошибка во время синхронизации: {e}')
            
            integration_settings.save()

        return redirect('admin_panel:integration_1c')

    context = {
        'title': 'Интеграция с 1С:Медицина',
        'subtitle': 'Управление подключением к 1С',
        'settings': integration_settings,
    }
    return render(request, 'admin/integrations/1c_medicine.html', context)


@staff_required
def zoom_integration_view(request):
    """
    Отображает страницу для управления настройками интеграции с Zoom.
    """
    integration_settings, created = ZoomIntegration.objects.get_or_create(id=1)

    if request.method == 'POST':
        integration_settings.name = request.POST.get('name', integration_settings.name)
        integration_settings.account_id = request.POST.get('account_id', integration_settings.account_id)
        integration_settings.client_id = request.POST.get('client_id', integration_settings.client_id)
        integration_settings.is_active = 'is_active' in request.POST

        client_secret = request.POST.get('client_secret')
        if client_secret:
            integration_settings.client_secret = client_secret
        
        integration_settings.save()
        messages.success(request, 'Настройки интеграции с Zoom успешно сохранены.')
        return redirect('admin_panel:integration_zoom')

    context = {
        'title': 'Интеграция с Zoom',
        'subtitle': 'Управление подключением к Zoom API',
        'settings': integration_settings,
    }
    return render(request, 'admin/integrations/zoom_integration.html', context)

class PatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Patient
    template_name = 'core/admin/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('curator').prefetch_related('admissions')
        
        # Search functionality
        self.search_query = self.request.GET.get('q', '')
        if self.search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=self.search_query) |
                Q(first_name__icontains=self.search_query) |
                Q(middle_name__icontains=self.search_query) |
                Q(phone_number__icontains=self.search_query) |
                Q(email__icontains=self.search_query) |
                Q(address__icontains=self.search_query)
            )
        
        # Filter by status
        self.status_filter = self.request.GET.get('status', '')
        if self.status_filter == 'admitted':
            queryset = queryset.filter(admissions__discharge_date__isnull=True)
        elif self.status_filter == 'discharged':
            queryset = queryset.filter(admissions__discharge_date__isnull=False)
        
        # Filter by gender
        self.gender_filter = self.request.GET.get('gender', '')
        if self.gender_filter in ['M', 'F']:
            queryset = queryset.filter(gender=self.gender_filter)
        
        # Filter by age group
        self.age_filter = self.request.GET.get('age', '')
        if self.age_filter == 'child':
            queryset = queryset.filter(age__lt=18)
        elif self.age_filter == 'adult':
            queryset = queryset.filter(age__range=(18, 65))
        elif self.age_filter == 'senior':
            queryset = queryset.filter(age__gt=65)
        
        # Ordering
        self.ordering = self.request.GET.get('ordering', 'last_name')
        if self.ordering in ['last_name', 'first_name', 'date_of_birth', 'created_at']:
            if self.ordering.startswith('-'):
                queryset = queryset.order_by(self.ordering)
            else:
                queryset = queryset.order_by(self.ordering)
        
        # Annotate with admission status
        queryset = queryset.annotate(
            is_admitted=Case(
                When(admissions__discharge_date__isnull=True, then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField()
            )
        )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter parameters to context
        context.update({
            'search_query': self.search_query,
            'status_filter': self.status_filter,
            'gender_filter': self.gender_filter,
            'age_filter': self.age_filter,
            'current_ordering': self.ordering,
            'total_patients': self.get_queryset().count(),
            'admitted_count': Patient.objects.filter(admissions__discharge_date__isnull=True).count(),
            'discharged_count': Patient.objects.filter(admissions__discharge_date__isnull=False).count(),
            'gender_choices': Patient.GENDER_CHOICES,
        })
        
        return context

patient_list = PatientListView.as_view()

class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Patient
    template_name = 'core/admin/patient_detail.html'
    context_object_name = 'patient'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Get current admission with related data
        current_admission = PatientAdmission.objects.filter(
            patient=patient,
            discharge_date__isnull=True
        ).select_related('bed__ward', 'doctor').first()
        
        # Get all admissions in reverse chronological order
        admission_history = PatientAdmission.objects.filter(
            patient=patient
        ).select_related('bed__ward', 'doctor').order_by('-admission_date')
        
        # Get patient documents with pagination
        documents = PatientDocument.objects.filter(
            patient=patient
        ).order_by('-uploaded_at')
        
        # Document form for uploads
        document_form = PatientDocumentForm()
        document_form.fields['document_type'].initial = 'other'
        
        # Admission form if needed
        admission_form = None
        if not current_admission:
            admission_form = PatientAdmissionForm()
            admission_form.fields['bed'].queryset = Bed.objects.filter(
                is_available=True
            ).select_related('ward')
        
        # Get related data
        related_patients = Patient.objects.filter(
            Q(phone_number=patient.phone_number) |
            Q(email=patient.email) |
            Q(address=patient.address)
        ).exclude(pk=patient.pk).distinct()
        
        # Get statistics
        total_admissions = admission_history.count()
        total_days = sum(
            (admission.discharge_date or timezone.now().date()) - admission.admission_date
            for admission in admission_history
            if admission.admission_date
        )
        
        context.update({
            'current_admission': current_admission,
            'admission_history': admission_history,
            'documents': documents,
            'document_form': document_form,
            'admission_form': admission_form,
            'related_patients': related_patients,
            'stats': {
                'total_admissions': total_admissions,
                'total_days': total_days.days if total_admissions > 0 else 0,
                'documents_count': documents.count(),
                'avg_stay_days': total_days.days // total_admissions if total_admissions > 0 else 0,
            },
            'now': timezone.now(),
        })
        
        return context

patient_detail_admin = PatientDetailView.as_view()

# @method_decorator(csrf_exempt, name='dispatch')
# class PatientDocumentUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
#     model = PatientDocument
#     form_class = PatientDocumentForm
#     
#     def test_func(self):
#         return self.request.user.is_staff
#     
#     def form_valid(self, form):
#         form.instance.uploaded_by = self.request.user
#         form.instance.patient_id = self.kwargs['pk']
#         self.object = form.save()
#         
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'document': {
#                     'id': self.object.id,
#                     'name': self.object.document.name.split('/')[-1],
#                     'type': self.object.get_document_type_display(),
#                     'uploaded_at': self.object.uploaded_at.strftime('%d.%m.%Y %H:%M'),
#                     'url': self.object.document.url,
#                 }
#             })
#         return super().form_valid(form)
#     
#     def form_invalid(self, form):
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': False,
#                 'errors': form.errors
#             }, status=400)
#         return super().form_invalid(form)
#     
#     def get_success_url(self):
#         return reverse('core:patient_detail_admin', kwargs={'pk': self.kwargs['pk']})

# @require_http_methods(['POST'])
# @login_required
# @staff_required
# def delete_document(request, pk):
#     document = get_object_or_404(PatientDocument, pk=pk)
#     patient_pk = document.patient.pk
#     document.delete()
#     messages.success(request, 'Документ успешно удален')
#     return redirect('admin_panel:patient_detail', pk=patient_pk)

# Admission Management - временно отключено
# @login_required
# @staff_required
# def create_admission(request):
#     pass

# @login_required  
# @staff_required
# def update_admission(request, pk):
#     pass

# @require_http_methods(['POST'])
# @login_required
# @staff_required
# def discharge_patient(request, pk):
#     admission = get_object_or_404(PatientAdmission, pk=pk)
#     patient_pk = admission.patient.pk
    
#     if not admission.discharge_date:
#         with transaction.atomic():
#             admission.discharge_date = timezone.now().date()
#             admission.discharged_by = request.user
#             admission.save()
            
#             # Mark bed as available
#             bed = admission.bed
#             bed.is_available = True
#             bed.save()
            
#             messages.success(request, 'Пациент успешно выписан')
    
#     return redirect('admin_panel:patient_detail', pk=patient_pk)

# API Endpoints
@login_required
@staff_required
def search_patients(request):
    """API endpoint for patient search with autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    patients = Patient.objects.filter(
        Q(last_name__icontains=query) |
        Q(first_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(passport_number__icontains=query)
    ).values('id', 'last_name', 'first_name', 'middle_name', 'date_of_birth')[:10]
    
    results = [{
        'id': p['id'],
        'text': f"{p['last_name']} {p['first_name']} {p.get('middle_name', '')} ({p['date_of_birth'].year if p['date_of_birth'] else 'н/д'})",
        'birth_date': p['date_of_birth'].strftime('%d.%m.%Y') if p['date_of_birth'] else 'н/д'
    } for p in patients]
    
    return JsonResponse({'results': results})
