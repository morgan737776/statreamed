import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from services.models import ServiceAppointment
from django.contrib.auth import get_user_model

# Модель для хранения ссылок на видеовстречи (Zoom/другое)
from django.db import models

class TelemedicineMeeting(models.Model):
    appointment = models.OneToOneField(ServiceAppointment, on_delete=models.CASCADE, related_name='telemedicine_meeting')
    meeting_id = models.CharField(max_length=128, unique=True)
    join_url = models.URLField()
    start_url = models.URLField()
    topic = models.CharField(max_length=255)
    status = models.CharField(max_length=32, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# API для создания/получения видеовстреч (пример для Zoom, можно адаптировать под другой сервис)
class TelemedicineMeetingCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            appointment = ServiceAppointment.objects.get(pk=appointment_id)
        except ServiceAppointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=404)
        # Пример запроса к Zoom API (реальный production-ключ и user_id должны быть в settings)
        zoom_url = getattr(settings, 'ZOOM_API_URL', 'https://api.zoom.us/v2/users/me/meetings')
        zoom_token = getattr(settings, 'ZOOM_JWT_TOKEN', 'demo-token')
        headers = {'Authorization': f'Bearer {zoom_token}', 'Content-Type': 'application/json'}
        data = {
            'topic': f'Видеоконсультация с {appointment.specialist.get_full_name()} для {appointment.client.get_full_name()}',
            'type': 2,
            'start_time': f"{appointment.appointment_date}T{appointment.start_time}",
            'duration': 60,
            'timezone': 'Europe/Moscow',
        }
        try:
            resp = requests.post(zoom_url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            meeting = resp.json()
            tm = TelemedicineMeeting.objects.create(
                appointment=appointment,
                meeting_id=meeting['id'],
                join_url=meeting['join_url'],
                start_url=meeting['start_url'],
                topic=meeting['topic'],
                status='scheduled',
            )
            return Response({'meeting': {
                'id': tm.meeting_id,
                'join_url': tm.join_url,
                'start_url': tm.start_url,
                'topic': tm.topic,
                'status': tm.status,
            }}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class TelemedicineMeetingDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            tm = TelemedicineMeeting.objects.get(appointment_id=appointment_id)
        except TelemedicineMeeting.DoesNotExist:
            return Response({'detail': 'Meeting not found'}, status=404)
        return Response({
            'id': tm.meeting_id,
            'join_url': tm.join_url,
            'start_url': tm.start_url,
            'topic': tm.topic,
            'status': tm.status,
        })
