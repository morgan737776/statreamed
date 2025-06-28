from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from . import views

app_name = 'emr'

urlpatterns = [
    # Dashboard
    path('', login_required(views.dashboard), name='dashboard'),
    
    # Patient URLs
    path('patients/', 
         login_required(views.PatientListView.as_view()), 
         name='patient_list'),
    path('patients/add/', 
         permission_required('emr.add_patient')(views.PatientCreateView.as_view()), 
         name='patient_create'),
    path('patients/<int:pk>/', 
         permission_required('emr.view_patient')(views.PatientDetailView.as_view()), 
         name='patient_detail'),
    path('patients/<int:pk>/edit/', 
         permission_required('emr.change_patient')(views.PatientUpdateView.as_view()), 
         name='patient_edit'),
    
    # Medical Record URLs
    path('patients/<int:patient_pk>/medical-record/edit/', 
         permission_required('emr.change_medicalrecord')(views.MedicalRecordUpdateView.as_view()), 
         name='medical_record_edit'),
    
    # Entry URLs
    path('patients/<int:patient_pk>/entries/add/', 
         permission_required('emr.add_medicalrecordentry')(views.EntryCreateView.as_view()), 
         name='entry_create'),
    path('entries/<int:pk>/edit/', 
         permission_required('emr.change_medicalrecordentry')(views.EntryUpdateView.as_view()), 
         name='entry_edit'),
    path('entries/<int:pk>/delete/', 
         permission_required('emr.delete_medicalrecordentry')(views.delete_entry), 
         name='entry_delete'),
    
    # API Endpoints
    path('api/patients/<int:pk>/', 
         login_required(views.get_patient_data), 
         name='api_patient_data'),
]
