from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['disease', 'diagnosis_date', 'notes']
        widgets = {
            'disease': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
