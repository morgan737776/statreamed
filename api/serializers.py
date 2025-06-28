from rest_framework import serializers
from core.models import Patient
from services.models import ServiceAppointment

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender', 'phone_number', 'email', 'address', 'status']

class ServiceAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAppointment
        fields = ['id', 'patient', 'specialist', 'date', 'time', 'status', 'service_type']
