from django import forms
from django_select2.forms import ModelSelect2Widget

from .models import Document
from core.models import Patient
from django.utils.translation import gettext_lazy as _

class PatientSelect2Widget(ModelSelect2Widget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'middle_name__icontains',
    ]

    def label_from_instance(self, obj):
        return obj.get_full_name()

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'patient', 'category', 'file', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'patient': PatientSelect2Widget(
                queryset=Patient.objects.all(),
                attrs={'class': 'form-control'}
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
