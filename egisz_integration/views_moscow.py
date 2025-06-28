from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from .serializers_moscow import (
    export_patient_to_fhir_moscow,
    export_encounter_to_fhir_moscow,
    export_service_to_fhir_moscow
)
from .moscow_gateway import send_fhir_resource
from .models import IntegrationLog
from patients.models import Patient
from inpatient.models import Encounter
from services.models import Service

@csrf_exempt
@require_POST
def send_patient_to_egisz_moscow(request, patient_id):
    try:
        patient = Patient.objects.get(pk=patient_id)
        fhir_json = export_patient_to_fhir_moscow(patient)
        result = send_fhir_resource('Patient', fhir_json)
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_patient',
            request_data=fhir_json,
            response_data=json.dumps(result),
            status='success',
            region='moscow',
            timestamp=timezone.now()
        )
        return JsonResponse({'result': 'ok', 'egisz_response': result})
    except Exception as e:
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_patient',
            request_data=request.body.decode(errors='ignore'),
            response_data=str(e),
            status='error',
            region='moscow',
            timestamp=timezone.now()
        )
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')

@csrf_exempt
@require_POST
def send_encounter_to_egisz_moscow(request, encounter_id):
    try:
        encounter = Encounter.objects.get(pk=encounter_id)
        fhir_json = export_encounter_to_fhir_moscow(encounter)
        result = send_fhir_resource('Encounter', fhir_json)
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_encounter',
            request_data=fhir_json,
            response_data=json.dumps(result),
            status='success',
            region='moscow',
            timestamp=timezone.now()
        )
        return JsonResponse({'result': 'ok', 'egisz_response': result})
    except Exception as e:
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_encounter',
            request_data=request.body.decode(errors='ignore'),
            response_data=str(e),
            status='error',
            region='moscow',
            timestamp=timezone.now()
        )
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')

@csrf_exempt
@require_POST
def send_service_to_egisz_moscow(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
        fhir_json = export_service_to_fhir_moscow(service)
        result = send_fhir_resource('ServiceRequest', fhir_json)
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_service',
            request_data=fhir_json,
            response_data=json.dumps(result),
            status='success',
            region='moscow',
            timestamp=timezone.now()
        )
        return JsonResponse({'result': 'ok', 'egisz_response': result})
    except Exception as e:
        IntegrationLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            operation='send_service',
            request_data=request.body.decode(errors='ignore'),
            response_data=str(e),
            status='error',
            region='moscow',
            timestamp=timezone.now()
        )
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
