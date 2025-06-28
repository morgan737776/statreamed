from django.urls import path
from .views import PatientRegistrationWizard

app_name = 'rehabilitation'

urlpatterns = [
    path('add/', PatientRegistrationWizard.as_view(), name='patient_add'),
]

