import xml.etree.ElementTree as ET
from django.utils import timezone
from services.models import ServiceAppointment

# Пример генерации XML-реестра услуг для ОМС (ФОМС)
def export_oms_registry(period_start, period_end, organization_code):
    root = ET.Element('Registry')
    header = ET.SubElement(root, 'Header')
    ET.SubElement(header, 'OrganizationCode').text = organization_code
    ET.SubElement(header, 'PeriodStart').text = str(period_start)
    ET.SubElement(header, 'PeriodEnd').text = str(period_end)
    services_el = ET.SubElement(root, 'Services')
    
    appointments = ServiceAppointment.objects.filter(
        appointment_date__gte=period_start,
        appointment_date__lte=period_end,
        service__is_oms=True
    )
    for app in appointments:
        service_el = ET.SubElement(services_el, 'Service')
        ET.SubElement(service_el, 'PatientId').text = str(app.client_id)
        ET.SubElement(service_el, 'ServiceCode').text = app.service.code
        ET.SubElement(service_el, 'Date').text = str(app.appointment_date)
        ET.SubElement(service_el, 'Specialist').text = app.specialist.get_full_name() if app.specialist else ''
        ET.SubElement(service_el, 'Price').text = str(app.service.price)
    return ET.tostring(root, encoding='utf-8', method='xml')
