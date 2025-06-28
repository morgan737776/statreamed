from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from core.models import IntegrationSettings
import zeep

# Пример интеграции с 1С:Бухгалтерия через SOAP (zeep)
# Для реальной работы потребуется корректный wsdl_url и авторизация

def get_1c_client():
    wsdl_url = getattr(settings, 'ONEC_WSDL_URL', 'https://1c.example.com/soap/Service?wsdl')
    return zeep.Client(wsdl=wsdl_url)

class OneCInvoiceSend(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Пример: отправка счета в 1С
        data = request.data
        try:
            client = get_1c_client()
            # Пример вызова метода 1С (название и параметры уточнить по WSDL)
            result = client.service.CreateInvoice(
                CustomerName=data.get('customer_name'),
                Amount=data.get('amount'),
                InvoiceDate=data.get('invoice_date'),
                Description=data.get('description', '')
            )
            return Response({'result': result}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class OneCInvoiceStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        try:
            client = get_1c_client()
            # Получение статуса счета
            status = client.service.GetInvoiceStatus(InvoiceID=invoice_id)
            return Response({'status': status}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
