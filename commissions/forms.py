from django import forms
from .models import SelectionCommitteeApplication, MedicalCommitteeConclusion
from core.widgets import BootstrapDatePickerInput, BootstrapDateTimePickerInput
from medical_codes.models import ICD10Code

class SelectionCommitteeApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем queryset для поля icd10_codes, чтобы отображать только некатегориальные коды
        self.fields['icd10_codes'].queryset = ICD10Code.objects.filter(is_category=False)
        
        # Группируем коды по категориям для удобного отображения
        categories = ICD10Code.objects.filter(is_category=True).order_by('code')
        choices = []
        
        for category in categories:
            # Находим подкатегории для текущей категории
            sub_codes = ICD10Code.objects.filter(
                code__startswith=category.code[:1],
                is_category=False,
                code__gte=category.code[:3] + '0',
                code__lte=category.code[4:] + '9'
            ).order_by('code')
            
            if sub_codes.exists():
                # Добавляем опцию группы с подкатегориями
                category_choices = [(str(code.id), str(code)) for code in sub_codes]
                choices.append((category.name, category_choices))
        
        # Обновляем choices для поля icd10_codes
        self.fields['icd10_codes'].choices = choices
        self.fields['icd10_codes'].widget.attrs.update({
            'class': 'form-control select2',
            'data-placeholder': 'Выберите коды МКБ-10',
            'multiple': 'multiple',
        })
    
    class Meta:
        model = SelectionCommitteeApplication
        fields = [
            'full_name', 'date_of_birth', 'phone_number', 'address', 
            'diagnosis', 'operator_comment', 'icd10_codes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': BootstrapDatePickerInput(),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'operator_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {
            'icd10_codes': 'Выберите один или несколько кодов МКБ-10, соответствующих диагнозу',
        }


class MedicalCommitteeConclusionForm(forms.ModelForm):
    class Meta:
        model = MedicalCommitteeConclusion
        fields = ['status', 'appointment_date', 'final_decision', 'committee_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': BootstrapDateTimePickerInput(),
            'final_decision': forms.Select(attrs={'class': 'form-select'}),
            'committee_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
