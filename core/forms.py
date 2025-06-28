from django import forms
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class UserEditForm(UserChangeForm):
    password = None  # скрыть поле пароля
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RoleChangeForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label='Роли (группы)'
    )

from django.db.models import Q
from .models import (
    Patient, MedicalRecord, PatientDocument,
    SystemSettings, IntegrationSettings, Staff
)

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = [
            'clinic_name', 'timezone', 'date_format', 'language',
            'maintenance_mode', 'logo', 'color_theme'
        ]
        widgets = {
            'clinic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_format': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'color_theme': forms.Select(attrs={'class': 'form-select'}),
        }

class IntegrationSettingsForm(forms.ModelForm):
    class Meta:
        model = IntegrationSettings
        fields = [
            'service_1c_url', 'service_1c_key', 'sms_provider', 'sms_api_key',
            'email_host', 'email_user', 'email_password', 'webhook_url'
        ]
        widgets = {
            'service_1c_url': forms.URLInput(attrs={'class': 'form-control'}),
            'service_1c_key': forms.TextInput(attrs={'class': 'form-control'}),
            'sms_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'sms_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'email_host': forms.TextInput(attrs={'class': 'form-control'}),
            'email_user': forms.TextInput(attrs={'class': 'form-control'}),
            'email_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'webhook_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'last_name', 'first_name', 'middle_name', 'date_of_birth', 'gender', 
            'address', 'phone', 'email', 'passport_series', 'passport_number',
            'insurance_policy', 'status', 'photo', 'emergency_contact_name',
            'emergency_contact_phone', 'allergies', 'chronic_diseases', 'blood_type'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_policy': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'chronic_diseases': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'title', 'content', 'priority', 'is_important']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientDocumentForm(forms.ModelForm):
    class Meta:
        model = PatientDocument
        fields = ['document_type', 'file', 'description', 'upload_date']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'upload_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class PatientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Поиск пациента',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ФИО, телефон, полис...',
            'hx-get': '/admin-panel/api/patients/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#search-results',
            'autocomplete': 'off'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        label='Статус',
        choices=(
            ('', 'Все'),
            ('admitted', 'На лечении'),
            ('discharged', 'Выписанные'),
        ),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/admin-panel/patients/',
            'hx-target': '#patient-list',
            'hx-push-url': 'true'
        })
    )
    
    gender = forms.ChoiceField(
        required=False,
        label='Пол',
        choices=(
            ('', 'Все'),
            ('M', 'Мужской'),
            ('F', 'Женский'),
        ),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/admin-panel/patients/',
            'hx-target': '#patient-list',
            'hx-push-url': 'true'
        })
    )
    
    age_group = forms.ChoiceField(
        required=False,
        label='Возрастная группа',
        choices=(
            ('', 'Все'),
            ('child', 'Дети (до 18)'),
            ('adult', 'Взрослые (18-65)'),
            ('senior', 'Пожилые (65+)'),
        ),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/admin-panel/patients/',
            'hx-target': '#patient-list',
            'hx-push-url': 'true'
        })
    )
    
    ordering = forms.ChoiceField(
        required=False,
        label='Сортировка',
        choices=(
            ('last_name', 'Фамилия (А-Я)'),
            ('-last_name', 'Фамилия (Я-А)'),
            ('-created_at', 'Дата добавления (новые)'),
            ('created_at', 'Дата добавления (старые)'),
        ),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/admin-panel/patients/',
            'hx-target': '#patient-list',
            'hx-push-url': 'true'
        })
    )
    
    def search(self, queryset):
        data = self.cleaned_data
        
        # Full-text search
        if data.get('q'):
            query = data['q']
            queryset = queryset.filter(
                Q(last_name__icontains=query) |
                Q(first_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(insurance_number__icontains=query)
            )
        
        # Status filter
        if data.get('status') == 'admitted':
            queryset = queryset.filter(admissions__discharge_date__isnull=True)
        elif data.get('status') == 'discharged':
            queryset = queryset.filter(admissions__discharge_date__isnull=False)
        
        # Gender filter
        if data.get('gender'):
            queryset = queryset.filter(gender=data['gender'])
        
        # Age group filter
        if data.get('age_group') == 'child':
            queryset = queryset.filter(age__lt=18)
        elif data.get('age_group') == 'adult':
            queryset = queryset.filter(age__range=(18, 65))
        elif data.get('age_group') == 'senior':
            queryset = queryset.filter(age__gt=65)
        
        # Ordering
        if data.get('ordering'):
            queryset = queryset.order_by(data['ordering'])
        
        return queryset.distinct()
