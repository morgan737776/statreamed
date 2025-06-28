from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.views import View
import datetime

from .models import Appointment
from services.models import ServiceAppointment

class CalendarView(View):
    template_name = 'core/calendar.html'
    
    def get(self, request):
        return render(request, self.template_name)

@login_required
@require_GET
def get_appointments(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    if not start or not end:
        return JsonResponse({'error': 'Missing start or end date'}, status=400)
    
    try:
        start_date = datetime.datetime.fromisoformat(start)
        end_date = datetime.datetime.fromisoformat(end)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Получаем все приемы в указанном диапазоне дат
    appointments = Appointment.objects.filter(
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    ).select_related('patient', 'doctor', 'service')
    
    # Получаем телемедицинские приемы
    telemedicine_appointments = ServiceAppointment.objects.filter(
        appointment_date__gte=start_date.date(),
        appointment_date__lte=end_date.date(),
        is_telemedicine=True
    ).select_related('client', 'service', 'specialist')
    
    events = []
    
    # Добавляем обычные приемы
    for appointment in appointments:
        events.append({
            'id': f'a{appointment.id}',
            'title': f'{appointment.service.name} - {appointment.patient.get_full_name()}',
            'start': appointment.start_datetime.isoformat(),
            'end': appointment.end_datetime.isoformat(),
            'backgroundColor': '#4CAF50' if appointment.status == 'completed' else '#FF9800',
            'borderColor': '#4CAF50' if appointment.status == 'completed' else '#FF9800',
            'extendedProps': {
                'type': 'regular',
                'patient': {
                    'id': appointment.patient.id,
                    'first_name': appointment.patient.first_name,
                    'last_name': appointment.patient.last_name
                },
                'doctor_name': appointment.doctor.get_full_name(),
                'service': appointment.service.name
            }
        })
    
    # Добавляем телемедицинские приемы
    for tele_app in telemedicine_appointments:
        start_time = datetime.datetime.combine(
            tele_app.appointment_date,
            tele_app.start_time
        )
        
        end_time = datetime.datetime.combine(
            tele_app.appointment_date,
            tele_app.end_time if tele_app.end_time else (tele_app.start_time + datetime.timedelta(minutes=30))
        )
        
        events.append({
            'id': f't{tele_app.id}',
            'title': f'Телемедицина - {tele_app.service.name} - {tele_app.client.get_full_name()}',
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'backgroundColor': '#2196F3',
            'borderColor': '#2196F3',
            'extendedProps': {
                'type': 'telemedicine',
                'patient': {
                    'id': tele_app.client.id,
                    'first_name': tele_app.client.first_name,
                    'last_name': tele_app.client.last_name
                },
                'doctor_name': tele_app.specialist.get_full_name(),
                'service': tele_app.service.name,
                'zoom_meeting_id': tele_app.zoom_meeting_id
            }
        })
    
    return JsonResponse(events, safe=False)

@login_required
def create_appointment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        try:
            start = datetime.datetime.fromisoformat(data['start'])
            end = datetime.datetime.fromisoformat(data['end'])
            
            if end <= start:
                return JsonResponse({'error': 'End time must be after start time'}, status=400)
            
            # Проверяем пересечение с другими приемами
            overlapping_appointments = Appointment.objects.filter(
                Q(start_datetime__lt=end, end_datetime__gt=start) &
                Q(doctor_id=data['doctor_id'])
            )
            
            if overlapping_appointments.exists():
                return JsonResponse({
                    'error': 'Время пересекается с другим приемом'
                }, status=400)
            
            appointment = Appointment.objects.create(
                patient_id=data['patient_id'],
                doctor_id=data['doctor_id'],
                service_id=data['service_id'],
                start_datetime=start,
                end_datetime=end,
                status='scheduled'
            )
            
            return JsonResponse({
                'id': appointment.id,
                'title': f'{appointment.service.name} - {appointment.patient.get_full_name()}',
                'start': appointment.start_datetime.isoformat(),
                'end': appointment.end_datetime.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def update_appointment(request, appointment_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Проверяем права доступа
            if appointment.doctor != request.user:
                return JsonResponse({'error': 'Нет прав для редактирования'}, status=403)
            
            start = datetime.datetime.fromisoformat(data['start'])
            end = datetime.datetime.fromisoformat(data['end'])
            
            if end <= start:
                return JsonResponse({'error': 'End time must be after start time'}, status=400)
            
            # Проверяем пересечение с другими приемами
            overlapping_appointments = Appointment.objects.filter(
                Q(start_datetime__lt=end, end_datetime__gt=start) &
                Q(doctor_id=appointment.doctor_id) &
                ~Q(id=appointment.id)
            )
            
            if overlapping_appointments.exists():
                return JsonResponse({
                    'error': 'Время пересекается с другим приемом'
                }, status=400)
            
            appointment.start_datetime = start
            appointment.end_datetime = end
            appointment.status = data.get('status', appointment.status)
            appointment.save()
            
            return JsonResponse({
                'id': appointment.id,
                'title': f'{appointment.service.name} - {appointment.patient.get_full_name()}',
                'start': appointment.start_datetime.isoformat(),
                'end': appointment.end_datetime.isoformat()
            })
            
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def delete_appointment(request, appointment_id):
    if request.method == 'DELETE':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Проверяем права доступа
            if appointment.doctor != request.user and not request.user.is_staff:
                return JsonResponse({'error': 'Нет прав для удаления'}, status=403)
            
            appointment.delete()
            return JsonResponse({'success': True})
            
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
