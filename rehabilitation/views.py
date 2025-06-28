from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from core.models import Patient
from .models import RehabilitationCard
from .forms import PatientCreationForm, RehabilitationCardForm

# Определяем названия для шагов
PATIENT_FORM_STEP = 'patient_info'
REHAB_CARD_STEP = 'rehab_card'

class PatientRegistrationWizard(SessionWizardView):
    form_list = [
        (PATIENT_FORM_STEP, PatientCreationForm),
        (REHAB_CARD_STEP, RehabilitationCardForm),
    ]
    # Указываем шаблоны для каждого шага
    def get_template_names(self):
        return [f'rehabilitation/wizard_step_{self.steps.current}.html']

    # Метод, который вызывается после успешного завершения всех шагов
    def done(self, form_list, **kwargs):
        # Собираем данные из всех форм
        form_data = self.get_all_cleaned_data()

        # 1. Создаем пациента
        patient = Patient.objects.create(
            username=f"{form_data['last_name'].lower()}_{form_data['first_name'].lower()}",
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            middle_name=form_data.get('middle_name', ''),
            date_of_birth=form_data['date_of_birth'],
            gender=form_data['gender'],
            phone_number=form_data['phone_number'],
            email=form_data['email'],
            address=form_data['address']
        )

        # 2. Создаем реабилитационную карту
        rehab_card = RehabilitationCard(
            patient=patient,
            card_number=form_data['card_number'], # Убедимся, что это поле есть в форме
            # ... и так далее для всех полей из RehabilitationCardForm
            clinic_name=form_data.get('clinic_name'),
            clinic_address=form_data.get('clinic_address'),
            clinic_ogrn=form_data.get('clinic_ogrn'),
            service_recipient_status=form_data.get('service_recipient_status'),
            course_start_date=form_data.get('course_start_date'),
            service_contract_number=form_data.get('service_contract_number'),
            service_contract_date=form_data.get('service_contract_date'),
            disability_group=form_data.get('disability_group'),
            ipra_number=form_data.get('ipra_number'),
            ipra_date=form_data.get('ipra_date'),
        )
        rehab_card.save()

        # Перенаправляем на страницу пациента
        return redirect('core:patient_detail', pk=patient.pk)

    # Можно добавить начальные данные для форм
    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == REHAB_CARD_STEP:
            # Предзаполняем данные клиники
            initial.update({
                'clinic_name': 'Наименование организации ГБУ «ДРеабилитационный центр»',
                'clinic_address': 'Адрес реабилитационной организации: г. Москва, ул. 1-я Радиаторская б-р, д. 1',
                'clinic_ogrn': 'ОГРН: 1077761168124, ОКТМО: 12345124, ОКВЭД: 123456-123456'
            })
        return initial

