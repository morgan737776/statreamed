from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.encounter import Encounter
from fhir.resources.servicerequest import ServiceRequest

def export_patient_to_fhir_moscow(patient):
    fhir_patient = FhirPatient(
        id=str(patient.pk),
        name=[{"family": patient.last_name, "given": [patient.first_name]}],
        birthDate=str(patient.birth_date),
        identifier=[
            {"system": "urn:oid:1.2.643.5.1.13.13.12.2.21.1", "value": getattr(patient, 'snils', '')},
            {"system": "urn:egisz:moscow:oms", "value": getattr(patient, 'oms', '')}
        ]
    )
    return fhir_patient.json()

def export_encounter_to_fhir_moscow(encounter):
    fhir_encounter = Encounter(
        id=str(encounter.pk),
        status="in-progress",
        class_fhir={"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP"},
        subject={"reference": f"Patient/{encounter.patient.pk}"},
        period={"start": encounter.start_date.isoformat()}
    )
    return fhir_encounter.json()

def export_service_to_fhir_moscow(service):
    fhir_service = ServiceRequest(
        id=str(service.pk),
        status="active",
        intent="order",
        subject={"reference": f"Patient/{service.patient.pk}"},
        code={"coding": [{"system": "urn:egisz:moscow:service", "code": service.code}]}
    )
    return fhir_service.json()
