from django.urls import path
from .api_views import ICD10SearchView, ServiceNomenclatureSearchView

urlpatterns = [
    path('icd10/search/', ICD10SearchView.as_view(), name='icd10_search'),
    path('services/search/', ServiceNomenclatureSearchView.as_view(), name='service_nomenclature_search'),
]
