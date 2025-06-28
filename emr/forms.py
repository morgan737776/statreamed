from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.models import Patient
from .models import MedicalRecord, MedicalRecordEntry, TestResult, Prescription

User = get_user_model()

class PatientRegistrationForm(UserCreationForm):
    """Форма регистрации пациента с расширенными полями"""
    first_name = forms.CharField(label=_('Имя'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Фамилия'), max_length=30, required=True)
    patronymic = forms.CharField(label=_('Отчество'), max_length=30, required=False)
    email = forms.EmailField(label=_('Электронная почта'), required=True)
    
    # Поля пациента
    insurance_number = forms.CharField(
        label=_('СНИЛС'),
        max_length=14,
        required=True,
        help_text=_('Формат: XXX-XXX-XXX XX')
    )
    
    phone = forms.CharField(
        label=_('Телефон'),
        max_length=20,
        required=True,
        help_text=_('Формат: +7XXXXXXXXXX')
    )
    
    birth_date = forms.DateField(
        label=_('Дата рождения'),
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'patronymic',
                  'password1', 'password2', 'insurance_number', 'phone', 'birth_date')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Создаем профиль пациента
            Patient.objects.create(
                user=user,
                insurance_number=self.cleaned_data['insurance_number'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date']
            )
        return user


class MedicalRecordForm(forms.ModelForm):
    """Форма для создания/редактирования медицинской карты"""
    class Meta:
        model = MedicalRecord
        fields = ['allergies', 'chronic_diseases', 'disability', 'disability_details']
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'disability': forms.Select(attrs={'class': 'form-select'}),
            'disability_details': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class MedicalRecordEntryForm(forms.ModelForm):
    """Форма для добавления записей в медицинскую карту"""
    class Meta:
        model = MedicalRecordEntry
        fields = ['entry_type', 'title', 'content', 'is_confidential', 'is_important']
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TestResultForm(forms.ModelForm):
    """Форма для добавления результатов анализов"""
    class Meta:
        model = TestResult
        fields = [
            'test_type', 'test_name', 'result_numeric', 'result_text', 
            'reference_range', 'unit', 'is_abnormal', 'result_file', 
            'collected_at', 'processed_at', 'notes'
        ]
        widgets = {
            'test_type': forms.Select(attrs={'class': 'form-select'}),
            'test_name': forms.TextInput(attrs={'class': 'form-control'}),
            'result_numeric': forms.NumberInput(attrs={'class': 'form-control'}),
            'result_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference_range': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'is_abnormal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'collected_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'processed_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class PrescriptionForm(forms.ModelForm):
    """Форма для назначений врача"""
    class Meta:
        model = Prescription
        fields = ['treatment_item', 'description', 'status', 'frequency', 'start_date', 
                 'end_date', 'is_prn', 'prn_reason']
        widgets = {
            'treatment_item': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'is_prn': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prn_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
