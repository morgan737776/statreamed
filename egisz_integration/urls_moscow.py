from django.urls import path
from . import views_moscow

urlpatterns = [
    path('moscow/patient/send/<int:patient_id>/', views_moscow.send_patient_to_egisz_moscow, name='send_patient_to_egisz_moscow'),
    path('moscow/encounter/send/<int:encounter_id>/', views_moscow.send_encounter_to_egisz_moscow, name='send_encounter_to_egisz_moscow'),
    path('moscow/service/send/<int:service_id>/', views_moscow.send_service_to_egisz_moscow, name='send_service_to_egisz_moscow'),
]
