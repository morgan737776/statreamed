from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ServiceAppointmentViewSet
from .fhir_views import FHIRPatientList, FHIRPatientDetail
from .hl7_views import HL7PatientList, HL7PatientDetail
from .egisz_views import EGISZPatientSend, EGISZPatientReceive
from .telemedicine_views import TelemedicineMeetingCreate, TelemedicineMeetingDetail
from .onec_views import OneCInvoiceSend, OneCInvoiceStatus

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'appointments', ServiceAppointmentViewSet)

urlpatterns = [
    # FHIR endpoints
    path('fhir/patients/', FHIRPatientList.as_view(), name='fhir-patient-list'),
    path('fhir/patients/<int:pk>/', FHIRPatientDetail.as_view(), name='fhir-patient-detail'),

    # HL7 endpoints
    path('hl7/patients/', HL7PatientList.as_view(), name='hl7-patient-list'),
    path('hl7/patients/<int:pk>/', HL7PatientDetail.as_view(), name='hl7-patient-detail'),

    # ЕГИСЗ endpoints
    path('egisz/patients/<int:pk>/send/', EGISZPatientSend.as_view(), name='egisz-patient-send'),
    path('egisz/patients/<int:pk>/receive/', EGISZPatientReceive.as_view(), name='egisz-patient-receive'),

    # Телемедицина (Zoom)
    path('telemedicine/appointments/<int:appointment_id>/create/', TelemedicineMeetingCreate.as_view(), name='telemedicine-meeting-create'),
    path('telemedicine/appointments/<int:appointment_id>/', TelemedicineMeetingDetail.as_view(), name='telemedicine-meeting-detail'),

    # 1С:Бухгалтерия
    path('onec/invoice/send/', OneCInvoiceSend.as_view(), name='onec-invoice-send'),
    path('onec/invoice/<str:invoice_id>/status/', OneCInvoiceStatus.as_view(), name='onec-invoice-status'),
] + router.urls
