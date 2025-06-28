from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from .export_oms import export_oms_registry

class OMSRegistryExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Параметры периода и организации через query params
        period_start = request.query_params.get('period_start', str(timezone.now().date().replace(day=1)))
        period_end = request.query_params.get('period_end', str(timezone.now().date()))
        organization_code = request.query_params.get('org', 'ORG001')
        xml_bytes = export_oms_registry(period_start, period_end, organization_code)
        response = HttpResponse(xml_bytes, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="oms_registry_{period_start}_{period_end}.xml"'
        return response
