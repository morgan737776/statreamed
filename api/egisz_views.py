import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from core.models import Patient

# Примерная структура для интеграции с ЕГИСЗ (Единая государственная информационная система в сфере здравоохранения)
# В реальной интеграции потребуется согласование форматов, авторизация, обработка ошибок и соответствие спецификациям ЕГИСЗ.

class EGISZPatientSend(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        # Пример формирования данных (адаптировать под требования ЕГИСЗ)
        data = {
            'id': str(patient.id),
            'last_name': patient.last_name,
            'first_name': patient.first_name,
            'middle_name': patient.middle_name,
            'gender': patient.gender,
            'birth_date': patient.birth_date.isoformat() if patient.birth_date else '',
            'phone': patient.phone,
            'document_number': getattr(patient, 'document_number', ''),
        }
        # Пример отправки (URL и авторизация должны быть заданы в settings или IntegrationSettings)
        egisz_url = getattr(settings, 'EGISZ_API_URL', 'https://egisz.example/api/patients/')
        egisz_token = getattr(settings, 'EGISZ_TOKEN', 'demo-token')
        headers = {'Authorization': f'Bearer {egisz_token}', 'Content-Type': 'application/json'}
        try:
            resp = requests.post(egisz_url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            return Response({'egisz_response': resp.json()}, status=resp.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class EGISZPatientReceive(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        egisz_url = getattr(settings, 'EGISZ_API_URL', 'https://egisz.example/api/patients/')
        egisz_token = getattr(settings, 'EGISZ_TOKEN', 'demo-token')
        headers = {'Authorization': f'Bearer {egisz_token}'}
        try:
            resp = requests.get(f'{egisz_url}{pk}/', headers=headers, timeout=10)
            resp.raise_for_status()
            return Response({'egisz_data': resp.json()}, status=resp.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
