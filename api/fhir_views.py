from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from fhir.resources.patient import Patient as FhirPatient
from fhir.resources.bundle import Bundle
from core.models import Patient

class FHIRPatientList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.all()
        entries = []
        for p in patients:
            fhir_patient = FhirPatient(
                id=str(p.id),
                name=[{'family': p.last_name, 'given': [p.first_name, p.middle_name or '']}],
                gender=p.gender,
                birthDate=p.birth_date.isoformat() if p.birth_date else None,
                telecom=[{'system': 'phone', 'value': p.phone}] if p.phone else None
            )
            entries.append({'resource': fhir_patient.dict()})
        bundle = Bundle(type='searchset', entry=entries)
        return Response(bundle.dict(), status=status.HTTP_200_OK)

class FHIRPatientDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            p = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        fhir_patient = FhirPatient(
            id=str(p.id),
            name=[{'family': p.last_name, 'given': [p.first_name, p.middle_name or '']}],
            gender=p.gender,
            birthDate=p.birth_date.isoformat() if p.birth_date else None,
            telecom=[{'system': 'phone', 'value': p.phone}] if p.phone else None
        )
        return Response(fhir_patient.dict(), status=200)
