from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SelectionCommitteeApplication, MedicalCommitteeConclusion
from core.models import Patient
from inpatient.models import AdmissionRequest
from .forms import SelectionCommitteeApplicationForm, MedicalCommitteeConclusionForm

class CommissionDashboardView(LoginRequiredMixin, ListView):
    model = SelectionCommitteeApplication
    template_name = 'commissions/dashboard.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        return SelectionCommitteeApplication.objects.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_applications = SelectionCommitteeApplication.objects.all()
        
        context['stats'] = {
            'new_applications': all_applications.filter(status='NEW').count(),
            'pending_appointment': all_applications.filter(status='IN_PROGRESS', appointment_date__isnull=True).count(),
            'total_active': all_applications.exclude(status__in=['COMPLETED', 'ARCHIVED', 'REJECTED']).count(),
        }
        return context

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = SelectionCommitteeApplication
    form_class = SelectionCommitteeApplicationForm
    template_name = 'commissions/application_form.html'
    success_url = reverse_lazy('commissions:dashboard')

    def form_valid(self, form):
        form.instance.operator = self.request.user
        messages.success(self.request, f"Заявка для {form.instance.full_name} успешно создана.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация нового обращения'
        context['title'] = 'Регистрация нового обращения'
        context['button_text'] = 'Сохранить заявку'
        return context

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = SelectionCommitteeApplication
    template_name = 'commissions/application_detail.html'
    context_object_name = 'app'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Пытаемся получить связанное заключение врачебной комиссии
        context['medical_conclusion'] = MedicalCommitteeConclusion.objects.filter(application=self.object).first()
        return context

class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = SelectionCommitteeApplication
    form_class = SelectionCommitteeApplicationForm
    template_name = 'commissions/application_form.html'
    success_url = reverse_lazy('commissions:dashboard')

    def form_valid(self, form):
        messages.success(self.request, f"Заявка для {form.instance.full_name} успешно обновлена.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование обращения'
        context['button_text'] = 'Сохранить изменения'
        return context


class AdmissionRequestCreatorMixin:
    """
    Миксин для автоматического создания заявок на госпитализацию.
    """
    def create_admission_request(self, application):
        # 1. Найти или создать пациента
        patient, created = Patient.objects.get_or_create(
            full_name=application.full_name,
            date_of_birth=application.date_of_birth,
            defaults={
                'phone_number': application.phone_number,
                'address': application.address,
            }
        )

        if created:
            messages.info(self.request, f"Создана новая карточка пациента: {patient.full_name}.")

        # 2. Проверить, нет ли уже активной заявки на госпитализацию
        if AdmissionRequest.objects.filter(patient=patient, status='WAITING').exists():
            messages.warning(self.request, f"У пациента {patient.full_name} уже есть активная заявка на госпитализацию.")
            return

        # 3. Создать заявку на госпитализацию
        notes = (f"Заявка создана автоматически из обращения в отборочную комиссию №{application.id}.\n"
                 f"Первичный диагноз: {application.diagnosis}\n"
                 f"Комментарий оператора: {application.operator_comment}")

        AdmissionRequest.objects.create(
            patient=patient,
            planned_admission_date=application.appointment_date,  # Используем дату из заявки
            notes=notes,
            status='WAITING',
            source_commission_application=application
        )
        messages.success(self.request, f"Автоматически создана заявка на госпитализацию для пациента {patient.full_name}.")


class MedicalCommitteeConclusionCreateView(LoginRequiredMixin, AdmissionRequestCreatorMixin, CreateView):
    model = MedicalCommitteeConclusion
    form_class = MedicalCommitteeConclusionForm
    template_name = 'commissions/medical_conclusion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = get_object_or_404(SelectionCommitteeApplication, pk=self.kwargs['app_pk'])
        context['title'] = f"Создание заключения для {context['application'].full_name}"
        # Проверка, чтобы не попасть на страницу создания, если заключение уже есть
        if hasattr(context['application'], 'medical_conclusion') and context['application'].medical_conclusion is not None:
            messages.warning(self.request, "Заключение для этой заявки уже существует. Вы можете его отредактировать.")
            # Этого не должно происходить, но на всякий случай перенаправляем
            # Этот код не будет выполнен, так как мы используем redirect в dispatch
        return context

    def dispatch(self, request, *args, **kwargs):
        application = get_object_or_404(SelectionCommitteeApplication, pk=self.kwargs['app_pk'])
        if hasattr(application, 'medical_conclusion') and application.medical_conclusion is not None:
            messages.warning(request, "Заключение для этой заявки уже существует. Вы можете его отредактировать.")
            return redirect('commissions:conclusion_edit', pk=application.medical_conclusion.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        application = get_object_or_404(SelectionCommitteeApplication, pk=self.kwargs['app_pk'])
        conclusion = form.save(commit=False)
        conclusion.application = application
        conclusion.save()

        if conclusion.final_decision == 'HOSPITALIZATION_RECOMMENDED':
            self.create_admission_request(application)

        messages.success(self.request, f"Заключение для {application.full_name} успешно создано.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('commissions:application_detail', kwargs={'pk': self.kwargs['app_pk']})


class MedicalCommitteeConclusionUpdateView(LoginRequiredMixin, AdmissionRequestCreatorMixin, UpdateView):
    model = MedicalCommitteeConclusion
    form_class = MedicalCommitteeConclusionForm
    template_name = 'commissions/medical_conclusion_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Редактирование заключения для {self.object.application.full_name}"
        return context

    def form_valid(self, form):
        conclusion = form.save()
        if conclusion.final_decision == 'HOSPITALIZATION_RECOMMENDED':
            self.create_admission_request(conclusion.application)
        messages.success(self.request, f"Заключение для {conclusion.application.full_name} успешно обновлено.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('commissions:application_detail', kwargs={'pk': self.object.application.pk})


class CommissionCalendarView(LoginRequiredMixin, TemplateView):
    """Отображает календарь с записями на комиссии."""
    template_name = 'commissions/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Календарь записей комиссий'
        return context


@login_required
def commission_events_api(request):
    """API эндпоинт для FullCalendar, отдает события в формате JSON."""
    events = []
    
    # Заявки отборочной комиссии (ОК)
    selection_apps = SelectionCommitteeApplication.objects.filter(appointment_date__isnull=False).exclude(status__in=['COMPLETED', 'REJECTED'])
    for app in selection_apps:
        events.append({
            'title': f'ОК: {app.full_name}',
            'start': app.appointment_date.isoformat(),
            'url': reverse('commissions:application_update', args=[app.pk]),
            'color': '#007bff',  # Синий
            'description': f'Статус: {app.get_status_display()}'
        })

    # Заключения врачебной комиссии (ВК)
    medical_conclusions = MedicalCommitteeConclusion.objects.filter(appointment_date__isnull=False).exclude(status='CONCLUDED')
    for conclusion in medical_conclusions:
        events.append({
            'title': f'ВК: {conclusion.application.full_name}',
            'start': conclusion.appointment_date.isoformat(),
            'url': reverse('commissions:conclusion_update', args=[conclusion.pk]),
            'color': '#28a745',  # Зеленый
            'description': f'Статус: {conclusion.get_status_display()}'
        })

    return JsonResponse(events, safe=False)


