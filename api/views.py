from rest_framework import viewsets, permissions
from core.models import Patient
from services.models import ServiceAppointment
from .serializers import PatientSerializer, ServiceAppointmentSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

class ServiceAppointmentViewSet(viewsets.ModelViewSet):
    queryset = ServiceAppointment.objects.all()
    serializer_class = ServiceAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
