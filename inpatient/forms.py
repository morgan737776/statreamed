# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _
from core.models import Patient
from django.db.models import Q
from .models import Bed, Hospitalization, AdmissionRequest, Ward

class HospitalizationForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(bed__isnull=True),
        label=_("Пациент"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bed = forms.ModelChoiceField(
        queryset=Bed.objects.filter(status='FREE'),
        label=_("Свободная койка"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def save(self):
        patient = self.cleaned_data['patient']
        bed = self.cleaned_data['bed']

        # Присваиваем пациента койке и меняем статус
        bed.patient = patient
        bed.status = 'OCCUPIED'
        bed.save()

        # Создаем запись в истории госпитализаций
        Hospitalization.objects.create(
            patient=patient,
            bed=bed
        )

        # Обновляем статус заявки в очереди, если она была
        admission_request = AdmissionRequest.objects.filter(patient=patient, status='WAITING').first()
        if admission_request:
            admission_request.status = 'FULFILLED'
            admission_request.save()

        return bed


class AdmissionRequestForm(forms.ModelForm):
    class Meta:
        model = AdmissionRequest
        fields = ['patient', 'requested_ward', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'requested_ward': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Пациенты, у которых нет койки И нет активной заявки в очереди
        waiting_patients_ids = AdmissionRequest.objects.filter(status='WAITING').values_list('patient_id', flat=True)
        self.fields['patient'].queryset = Patient.objects.filter(bed__isnull=True).exclude(id__in=waiting_patients_ids)
        self.fields['patient'].label = "Пациент (не госпитализирован и не в очереди)"
        self.fields['requested_ward'].label = "Желаемая палата (необязательно)"
        self.fields['notes'].label = "Примечания (например, требуемые условия)"
