from django import forms
from core.models import Patient
from .models import RehabilitationCard
from django_select2.forms import Select2Widget, Select2MultipleWidget

class PatientCreationForm(forms.ModelForm):
    # Явно определяем поле, чтобы задать формат ввода
    date_of_birth = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'text', 'placeholder': 'дд.мм.гггг'}),
        input_formats=['%d.%m.%Y']  # Указываем Django, как парсить дату
    )

    class Meta:
        model = Patient
        fields = [
            'last_name', 
            'first_name', 
            'middle_name', 
            'date_of_birth', 
            'gender', 
            'phone', 
            'email', 
            'address'
        ]
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество (при наличии)',
        }

class RehabilitationCardForm(forms.ModelForm):
    class Meta:
        model = RehabilitationCard
        fields = [
            # Сведения о клинике
            'clinic_name', 'clinic_address', 'clinic_ogrn',
            # Раздел 1: Диагнозы
            'primary_diagnosis', 'primary_diagnosis_icd10', 'concomitant_diagnosis', 'complications',
            # Раздел 2: Реабилитационный диагноз (по МКФ)
            'rehab_diagnosis_b', 'rehab_diagnosis_s', 'rehab_diagnosis_d', 'environmental_factors',
            # Раздел 3: Цели реабилитации
            'long_term_goal', 'short_term_goals',
            # Раздел 4: Команда
            'rehab_team',
            # Раздел 5: План
            'rehab_plan',
        ]
        widgets = {
            'primary_diagnosis': forms.Textarea(attrs={'rows': 3}),
            'concomitant_diagnosis': forms.Textarea(attrs={'rows': 3}),
            'complications': forms.Textarea(attrs={'rows': 3}),

            'environmental_factors': forms.Textarea(attrs={'rows': 4}),
            'long_term_goal': forms.Textarea(attrs={'rows': 3}),
            'short_term_goals': forms.Textarea(attrs={'rows': 4}),
            'rehab_team': forms.Textarea(attrs={'rows': 4}),
            'rehab_plan': forms.Textarea(attrs={'rows': 6}),
            'primary_diagnosis_icd10': Select2Widget(attrs={'data-width': '100%'}),
            'rehab_diagnosis_b': Select2MultipleWidget(attrs={'data-width': '100%'}),
            'rehab_diagnosis_s': Select2MultipleWidget(attrs={'data-width': '100%'}),
            'rehab_diagnosis_d': Select2MultipleWidget(attrs={'data-width': '100%'}),
        }
