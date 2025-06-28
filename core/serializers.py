from rest_framework import serializers
from .models import Appointment, Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'middle_name']

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor_name', 'start_datetime', 'end_datetime', 'title']
        
    def get_doctor_name(self, obj):
        return obj.doctor.get_full_name() if obj.doctor else ''
