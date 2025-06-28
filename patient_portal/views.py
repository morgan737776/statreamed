# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from core.models import Patient
from medical_history.models import MedicalRecord
from rehab_programs.models import ScheduledActivity


@login_required
def dashboard(request):
    """
    Отображает личный кабинет пациента с расписанием, медицинскими записями и документами.
    """
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        return HttpResponseForbidden("Доступ запрещен. Эта страница только для пациентов.")

    # 1. Предстоящие процедуры
    upcoming_activities = ScheduledActivity.objects.filter(
        program__patient=patient,
        scheduled_date__gte=timezone.now()
    ).select_related('program', 'specialist').order_by('scheduled_date')

    # 2. Медицинские записи
    medical_records = MedicalRecord.objects.filter(patient=patient).select_related('doctor').order_by('-date_of_visit')

    # 3. Документы пациента
    patient_documents = PatientDocument.objects.filter(patient=patient).order_by('-uploaded_at')

    context = {
        'patient': patient,
        'upcoming_activities': upcoming_activities,
        'medical_records': medical_records,
        'patient_documents': patient_documents,
    }
    return render(request, 'patient_portal/dashboard.html', context)
