from django.urls import path
from .api_export import OMSRegistryExportView

urlpatterns = [
    path('oms_registry/export/', OMSRegistryExportView.as_view(), name='oms_registry_export'),
]
