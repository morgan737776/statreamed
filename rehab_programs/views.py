# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from core.models import Patient
from .models import RehabilitationProgram, ScheduledActivity
from .forms import RehabilitationProgramForm, ScheduledActivityForm
from django.views.generic import ListView
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView, UpdateView, DeleteView

# ---
# CRUD для ScheduledActivity (действия календаря)
class ScheduledActivityCreateView(LoginRequiredMixin, CreateView):
    model = ScheduledActivity
    form_class = ScheduledActivityForm
    template_name = 'rehab_programs/scheduled_activity_form.html'

    def get_initial(self):
        initial = super().get_initial()
        program_id = self.request.GET.get('program')
        if program_id:
            initial['program'] = program_id
        return initial

    def get_success_url(self):
        return reverse_lazy('rehab_programs:calendar')

class ScheduledActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = ScheduledActivity
    form_class = ScheduledActivityForm
    template_name = 'rehab_programs/scheduled_activity_form.html'

    def get_success_url(self):
        return reverse_lazy('rehab_programs:calendar')

class ScheduledActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = ScheduledActivity
    template_name = 'rehab_programs/scheduled_activity_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('rehab_programs:calendar')

# ---
# NEW CLASS-BASED VIEWS FOR FULL CRUD

class RehabilitationProgramListView(LoginRequiredMixin, ListView):
    model = RehabilitationProgram
    template_name = 'rehab_programs/rehab_program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = Patient.objects.all().order_by('last_name', 'first_name')
        context['form'] = RehabilitationProgramForm()
        return context

class RehabilitationProgramCreateView(LoginRequiredMixin, CreateView):
    model = RehabilitationProgram
    form_class = RehabilitationProgramForm
    template_name = 'rehab_programs/rehab_program_form.html'
    success_url = reverse_lazy('rehab_programs:rehab_program_list')

class RehabilitationProgramUpdateView(LoginRequiredMixin, UpdateView):
    model = RehabilitationProgram
    form_class = RehabilitationProgramForm
    template_name = 'rehab_programs/rehab_program_form.html'
    success_url = reverse_lazy('rehab_programs:rehab_program_list')

class RehabilitationProgramDeleteView(LoginRequiredMixin, DeleteView):
    model = RehabilitationProgram
    template_name = 'rehab_programs/rehab_program_confirm_delete.html'
    success_url = reverse_lazy('rehab_programs:rehab_program_list')

from django.template.loader import render_to_string

from django.template.loader import render_to_string
from django.http import JsonResponse

@login_required
def add_rehab_program(request):
    if request.method == 'POST':
        form = RehabilitationProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                program_html = render_to_string('rehab_programs/partials/program_row.html', {'program': program})
                return JsonResponse({'success': True, 'program_html': program_html})
            return redirect('rehab_programs:rehab_program_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('rehab_programs:rehab_program_list')



@login_required
def rehab_program_detail(request, program_pk):
    program = get_object_or_404(RehabilitationProgram, pk=program_pk)
    scheduled_activities = program.scheduled_activities.all()
    form = ScheduledActivityForm()
    
    context = {
        'program': program,
        'scheduled_activities': scheduled_activities,
        'form': form
    }
    return render(request, 'rehab_programs/rehab_program_detail.html', context)


@login_required
def add_scheduled_activity(request, program_pk):
    program = get_object_or_404(RehabilitationProgram, pk=program_pk)
    if request.method == 'POST':
        form = ScheduledActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.program = program
            activity.save()
            return redirect('rehab_programs:rehab_program_detail', program_pk=program.pk)
    
    return redirect('rehab_programs:rehab_program_detail', program_pk=program.pk)


@login_required
def calendar_view(request):
    specialists = User.objects.filter(is_staff=True).order_by('last_name', 'first_name')
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    context = {
        'specialists': specialists,
        'patients': patients,
        'calendar_api_url': reverse('rehab_programs:calendar_api'),
    }
    return render(request, 'rehab_programs/calendar.html', context)


from datetime import timedelta
import json

@login_required
def calendar_api(request):
    # GET: Отдаем события для календаря
    if request.method == 'GET':
        specialist_id = request.GET.get('specialist_id')
        patient_id = request.GET.get('patient_id')
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        activities = ScheduledActivity.objects.select_related(
            'activity', 'program__patient', 'specialist'
        ).all()

        if specialist_id:
            activities = activities.filter(specialist_id=specialist_id)
        if patient_id:
            activities = activities.filter(program__patient_id=patient_id)
        if start_str and end_str:
            activities = activities.filter(
                scheduled_date__gte=start_str,
                scheduled_date__lte=end_str
            )

        events = []
        for activity in activities:
            end_time = activity.scheduled_date + timedelta(minutes=activity.activity.default_duration)
            events.append({
                'id': activity.id,
                'title': f"{activity.activity.name} - {activity.program.patient.get_full_name()}",
                'start': activity.scheduled_date.isoformat(),
                'end': end_time.isoformat(),
                'extendedProps': {
                    'specialist': activity.specialist.get_full_name() if activity.specialist else 'Не назначен',
                    'patient': activity.program.patient.get_full_name(),
                    'program_id': activity.program.id,
                }
            })
        return JsonResponse(events, safe=False)

    # POST: Создаем новое событие
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            program = get_object_or_404(RehabilitationProgram, pk=data['program_id'])
            activity_type = get_object_or_404(RehabActivity, pk=data['activity_id'])
            
            new_activity = ScheduledActivity.objects.create(
                program=program,
                activity=activity_type,
                scheduled_date=data['start'],
                specialist_id=data.get('specialist_id'),
                status='PLANNED'
            )
            return JsonResponse({'status': 'success', 'event_id': new_activity.id}, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid data: {e}'}, status=400)

    # PUT: Обновляем событие (drag-and-drop, resize)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            activity = get_object_or_404(ScheduledActivity, pk=data['id'])
            activity.scheduled_date = data['start']
            # Если передается ID специалиста, обновляем и его
            if 'specialist_id' in data:
                activity.specialist_id = data['specialist_id']
            activity.save()
            return JsonResponse({'status': 'success'})
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid data: {e}'}, status=400)

    # DELETE: Удаляем событие
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            activity = get_object_or_404(ScheduledActivity, pk=data['id'])
            activity.delete()
            return JsonResponse({'status': 'success'})
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid data: {e}'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
