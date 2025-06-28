from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.dates import MonthArchiveView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from core.models import Patient
from .models import MedicalRecord, MedicalRecordEntry, TestResult, Prescription
from .forms import (
    PatientRegistrationForm, MedicalRecordForm, MedicalRecordEntryForm,
    TestResultForm, PrescriptionForm
)

User = get_user_model()

# Patient Views
class PatientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Patient
    template_name = 'emr/patient_list.html'
    context_object_name = 'patients'
    permission_required = 'emr.view_patient'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        
        # Фильтрация по поисковому запросу
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(insurance_number__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        return queryset.order_by(sort_by)


class PatientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Patient
    template_name = 'emr/patient_detail.html'
    context_object_name = 'patient'
    permission_required = 'emr.view_patient'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Получаем последние записи для вкладок
        context['medical_record'] = getattr(patient, 'medical_record', None)
        context['recent_entries'] = MedicalRecordEntry.objects.filter(
            medical_record=context['medical_record']
        ).order_by('-created_at')[:5] if context['medical_record'] else []
        
        context['recent_tests'] = TestResult.objects.filter(
            medical_record=context['medical_record']
        ).order_by('-collected_at')[:5] if context['medical_record'] else []
        
        context['active_prescriptions'] = Prescription.objects.filter(
            medical_record=context['medical_record'],
            status='active'
        ).order_by('-created_at')[:5] if context['medical_record'] else []
        
        return context


class PatientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = PatientRegistrationForm
    template_name = 'emr/patient_form.html'
    permission_required = 'emr.add_patient'
    success_url = reverse_lazy('emr:patient_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Пациент успешно зарегистрирован'))
        return response


class PatientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Patient
    fields = ['insurance_number', 'phone', 'blood_type', 'rh_factor', 'work_place', 'notes']
    template_name = 'emr/patient_form.html'
    permission_required = 'emr.change_patient'
    
    def get_success_url(self):
        return reverse_lazy('emr:patient_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Данные пациента обновлены'))
        return response


# Medical Record Views
class MedicalRecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'emr/medical_record_form.html'
    permission_required = 'emr.change_medicalrecord'
    
    def get_success_url(self):
        return reverse_lazy('emr:patient_detail', kwargs={'pk': self.object.patient.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Медицинская карта обновлена'))
        return response


# Medical Record Entry Views
class EntryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MedicalRecordEntry
    form_class = MedicalRecordEntryForm
    template_name = 'emr/entry_form.html'
    permission_required = 'emr.add_medicalrecordentry'
    
    def get_initial(self):
        initial = super().get_initial()
        medical_record = get_object_or_404(MedicalRecord, patient_id=self.kwargs['patient_pk'])
        initial['medical_record'] = medical_record
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(Patient, pk=self.kwargs['patient_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.medical_record = get_object_or_404(MedicalRecord, patient_id=self.kwargs['patient_pk'])
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Запись успешно добавлена'))
        return response
    
    def get_success_url(self):
        return reverse_lazy('emr:patient_detail', kwargs={'pk': self.kwargs['patient_pk']})


class EntryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = MedicalRecordEntry
    form_class = MedicalRecordEntryForm
    template_name = 'emr/entry_form.html'
    permission_required = 'emr.change_medicalrecordentry'
    
    def get_success_url(self):
        return reverse_lazy('emr:patient_detail', kwargs={'pk': self.object.medical_record.patient.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Запись обновлена'))
        return response


@login_required
@require_http_methods(['DELETE'])
def delete_entry(request, pk):
    entry = get_object_or_404(MedicalRecordEntry, pk=pk)
    
    # Проверка прав доступа
    if not (request.user.has_perm('emr.delete_medicalrecordentry') or 
            entry.created_by == request.user):
        return HttpResponseForbidden()
    
    patient_pk = entry.medical_record.patient.pk
    entry.delete()
    messages.success(request, _('Запись удалена'))
    return JsonResponse({'success': True, 'redirect': reverse_lazy('emr:patient_detail', kwargs={'pk': patient_pk})})


# API Views
@login_required
def get_patient_data(request, pk):
    """API для получения данных пациента в JSON формате"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if not request.user.has_perm('emr.view_patient'):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = {
        'id': patient.pk,
        'full_name': str(patient),
        'insurance_number': patient.insurance_number,
        'birth_date': patient.birth_date.strftime('%d.%m.%Y') if patient.birth_date else None,
        'age': patient.age if hasattr(patient, 'age') else None,
        'blood_type': patient.get_blood_type_display() if patient.blood_type else None,
        'rh_factor': patient.get_rh_factor_display() if patient.rh_factor is not None else None,
    }
    
    return JsonResponse(data)


# Dashboard View
@login_required
def dashboard(request):
    """Главная страница ЭМК"""
    context = {}
    
    if request.user.has_perm('emr.view_patient'):
        # Для медперсонала - статистика и последние пациенты
        recent_patients = Patient.objects.select_related('user').order_by('-created_at')[:5]
        context['recent_patients'] = recent_patients
    else:
        # Для пациентов - их собственная информация
        try:
            patient = Patient.objects.get(user=request.user)
            context['patient'] = patient
            
            # Получаем последние записи
            if hasattr(patient, 'medical_record'):
                context['recent_entries'] = MedicalRecordEntry.objects.filter(
                    medical_record=patient.medical_record
                ).order_by('-created_at')[:5]
                
                context['upcoming_appointments'] = []  # Здесь можно добавить логику для получения предстоящих приемов
        except Patient.DoesNotExist:
            pass
    
    return render(request, 'emr/dashboard.html', context)
