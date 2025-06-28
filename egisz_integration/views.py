from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import export_patient_to_fhir
from .hl7_client import export_patient_to_hl7
from patients.models import Patient

@csrf_exempt
def patient_fhir_export(request, patient_id):
    patient = Patient.objects.get(pk=patient_id)
    fhir_json = export_patient_to_fhir(patient)
    return JsonResponse(fhir_json, safe=False)

@csrf_exempt
def patient_hl7_export(request, patient_id):
    patient = Patient.objects.get(pk=patient_id)
    hl7_msg = export_patient_to_hl7(patient)
    return JsonResponse({'hl7': hl7_msg})
