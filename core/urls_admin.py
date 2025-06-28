from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views_admin

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views_admin.admin_dashboard, name='dashboard'),
    
    # Patients
    path('patients/', views_admin.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views_admin.patient_detail_admin, name='patient_detail'),
    
    # Documents - временно отключено
    # path('patients/<int:pk>/documents/upload/', 
    #      views_admin.PatientDocumentUploadView.as_view(), 
    #      name='upload_document'),
    # path('documents/<int:pk>/delete/', 
    #      views_admin.delete_document, 
    #      name='delete_document'),
    
    # Admissions - временно отключено
    # path('admissions/create/', 
    #      views_admin.create_admission, 
    #      name='create_admission'),
    # path('admissions/<int:pk>/update/', 
    #      views_admin.update_admission, 
    #      name='update_admission'),
    # path('admissions/<int:pk>/discharge/', 
    #      views_admin.discharge_patient, 
    #      name='discharge_patient'),
    
    # API Endpoints
    # path('api/wards/<int:ward_id>/beds/', 
    #      views_admin.get_available_beds, 
    #      name='api_ward_beds'),
    path('api/patients/search/', 
         views_admin.search_patients, 
         name='api_patient_search'),

    # Integrations
    path('integrations/1c-medicine/', views_admin.integration_1c_medicine_view, name='integration_1c_medicine'),
    path('integrations/zoom/', views_admin.zoom_integration_view, name='integration_zoom'),
]    # Add more admin URLs here
