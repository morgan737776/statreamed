from django import forms
from django.forms import ModelForm
from .models import ICD10Code

class ICD10CodeForm(forms.Form):
    """Форма для выбора кодов МКБ-10"""
    icd10_codes = forms.ModelMultipleChoiceField(
        queryset=ICD10Code.objects.filter(is_category=False),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        label='Коды МКБ-10',
        required=False,
        help_text='Выберите один или несколько кодов МКБ-10'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Группируем коды по категориям для удобства выбора
        categories = ICD10Code.objects.filter(is_category=True).order_by('code')
        choices = []
        
        for category in categories:
            sub_codes = ICD10Code.objects.filter(
                code__startswith=category.code[:1],
                is_category=False,
                code__gte=category.code[:3] + '0',
                code__lte=category.code[4:] + '9'
            ).order_by('code')
            
            if sub_codes.exists():
                category_choices = [(code.id, str(code)) for code in sub_codes]
                choices.append((category.name, category_choices))
        
        self.fields['icd10_codes'].choices = choices
