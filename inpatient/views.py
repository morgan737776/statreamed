# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Ward, Bed, Hospitalization, AdmissionRequest
from django.utils import timezone
from .forms import HospitalizationForm, AdmissionRequestForm

@login_required
def dashboard(request):
    """
    Отображает панель управления стационаром с информацией о палатах и койках.
    """
    # Получаем все палаты и для каждой палаты получаем связанные с ней койки
    wards = Ward.objects.prefetch_related('beds__patient').all()
    free_beds_count = Bed.objects.filter(status='FREE').count()
    occupied_beds_count = Bed.objects.filter(status='OCCUPIED').count()
    admission_requests = AdmissionRequest.objects.filter(status='WAITING').select_related('patient', 'requested_ward')

    context = {
        'wards': wards,
        'free_beds_count': free_beds_count,
        'occupied_beds_count': occupied_beds_count,
        'admission_requests': admission_requests,
    }
    return render(request, 'inpatient/dashboard.html', context)

@login_required
def hospitalize_patient(request):
    """
    Обрабатывает госпитализацию пациента.
    """
    if request.method == 'POST':
        form = HospitalizationForm(request.POST)
        if form.is_valid():
            bed = form.save()
            messages.success(request, f'Пациент {bed.patient.get_full_name()} успешно госпитализирован.')
            return redirect('inpatient:dashboard')
    else:
        initial_data = {}
        patient_id = request.GET.get('patient_id')
        if patient_id:
            initial_data['patient'] = patient_id
        
        form = HospitalizationForm(initial=initial_data)

    context = {
        'form': form,
    }
    return render(request, 'inpatient/hospitalize_patient.html', context)

@login_required
def add_admission_request(request):
    if request.method == 'POST':
        form = AdmissionRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пациент успешно добавлен в очередь на госпитализацию.')
            return redirect('inpatient:dashboard')
    else:
        form = AdmissionRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'inpatient/add_admission_request.html', context)

@login_required
def gantt_chart_view(request):
    """
    Отображает страницу с диаграммой Ганта для стационара.
    """
    return render(request, 'inpatient/gantt_chart.html')

@login_required
def gantt_data_api(request):
    """
    Предоставляет данные для диаграммы Ганта в формате JSON.
    """
    data = []
    today = date.today()

    # 1. Текущие госпитализации
    active_hospitalizations = Hospitalization.objects.filter(is_active=True).select_related('patient', 'bed', 'bed__ward')
    for h in active_hospitalizations:
        data.append({
            "id": f"hosp_{h.id}",
            "name": h.patient.get_full_name(),
            "resource": f"{h.bed.ward.name} - Койка {h.bed.bed_number}",
            "start": h.date_admitted.date().isoformat(),
            "end": (today + timedelta(days=1)).isoformat(), # Ongoing
            "progress": 100,
        })

    # 2. Запланированные госпитализации
    planned_admissions = AdmissionRequest.objects.filter(
        status='WAITING',
        bed__isnull=False,
        planned_admission_date__isnull=False,
        planned_discharge_date__isnull=False
    ).select_related('patient', 'bed', 'bed__ward')

    for req in planned_admissions:
        data.append({
            "id": f"req_{req.id}",
            "name": f"План: {req.patient.get_full_name()}",
            "resource": f"{req.bed.ward.name} - Койка {req.bed.bed_number}",
            "start": req.planned_admission_date.isoformat(),
            "end": req.planned_discharge_date.isoformat(),
            "progress": 0,
        })
    
    return JsonResponse(data, safe=False)

@login_required
@require_POST
def discharge_patient(request, bed_id):
    """
    Обрабатывает выписку пациента с койки.
    """
    try:
        bed = Bed.objects.get(pk=bed_id, patient__isnull=False)
        patient_name = bed.patient.get_full_name()
        # Находим и деактивируем запись о госпитализации
        hospitalization_record = Hospitalization.objects.filter(bed=bed, is_active=True).first()
        if hospitalization_record:
            hospitalization_record.date_discharged = timezone.now()
            hospitalization_record.is_active = False
            hospitalization_record.save()

        # Освобождаем койку
        bed.patient = None
        bed.status = 'FREE'
        bed.save()
        messages.success(request, f'Пациент {patient_name} успешно выписан. Койка {bed.bed_number} в палате {bed.ward.name} теперь свободна.')
    except Bed.DoesNotExist:
        messages.error(request, 'Не удалось найти указанную койку или она уже свободна.')
    
    return redirect('inpatient:dashboard')
