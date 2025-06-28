from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Patient
from .models import MedicalRecord
from .forms import MedicalRecordForm

@login_required
def add_medical_record(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()
            return redirect('core:patient_detail', pk=patient.pk)
    # This view only handles POST, so we redirect on GET
    return redirect('core:patient_detail', pk=patient.pk)
