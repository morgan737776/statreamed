"""
Модуль интеграции с ЕГИСЗ Москвы: отправка FHIR-ресурсов (пациенты, госпитализации, услуги)
"""
import requests
from django.conf import settings
from .moscow_auth import get_moscow_egisz_token

FHIR_ENDPOINTS = {
    'Patient': 'Patient/',
    'Encounter': 'Encounter/',
    'ServiceRequest': 'ServiceRequest/',
}

def send_fhir_resource(resource_type, fhir_json):
    token = get_moscow_egisz_token()
    url = settings.EGISZ_MOSCOW_API_URL + FHIR_ENDPOINTS[resource_type]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json"
    }
    response = requests.post(url, data=fhir_json, headers=headers, verify=True)
    response.raise_for_status()
    return response.json()
