from django.urls import path
from . import views

urlpatterns = [
    path('fhir/patient/<int:patient_id>/', views.patient_fhir_export, name='patient_fhir_export'),
    path('hl7/patient/<int:patient_id>/', views.patient_hl7_export, name='patient_hl7_export'),
]
