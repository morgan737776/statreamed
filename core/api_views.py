from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
import json

from services.models import ServiceAppointment

@login_required
def get_patients(request):
    patients = Patient.objects.all()
    patient_list = []
    
    for patient in patients:
        patient_list.append({
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'full_name': f'{patient.last_name} {patient.first_name}'
        })
    
    return JsonResponse(patient_list, safe=False)

@login_required
def get_doctors(request):
    doctors = User.objects.filter(groups__name='Doctors')
    doctor_list = []
    
    for doctor in doctors:
        doctor_list.append({
            'id': doctor.id,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'full_name': f'{doctor.last_name} {doctor.first_name}'
        })
    
    return JsonResponse(doctor_list, safe=False)

@login_required
def get_services(request):
    services = ServiceItem.objects.filter(is_active=True)
    service_list = []
    
    for service in services:
        service_list.append({
            'id': service.id,
            'name': service.name,
            'category': service.category.name if service.category else None,
            'price': float(service.price)
        })
    
    return JsonResponse(service_list, safe=False)
