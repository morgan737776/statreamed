from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('upload/', views.DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/approve/', views.approve_document, name='document_approve'),
    path('<int:pk>/archive/', views.archive_document, name='document_archive'),
    path('<int:pk>/generate-pdf/', views.generate_document_pdf, name='document_generate_pdf'),
]
