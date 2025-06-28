from fhir.resources.patient import Patient as FhirPatient

def export_patient_to_fhir(patient):
    fhir_patient = FhirPatient(
        id=str(patient.pk),
        name=[{"family": patient.last_name, "given": [patient.first_name]}],
        birthDate=str(patient.birth_date),
        identifier=[{"system": "urn:oid:1.2.643.5.1.13.13.12.2.21.1", "value": getattr(patient, 'snils', '')}]
    )
    return fhir_patient.json()
