from django.urls import path
from . import views

app_name = 'medical_history'

urlpatterns = [
    path('patient/<int:patient_pk>/add_record/', views.add_medical_record, name='add_medical_record'),
]
