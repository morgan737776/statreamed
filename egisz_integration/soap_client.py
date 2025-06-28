from zeep import Client

def send_patient_to_egisz(patient_data):
    wsdl = 'https://egisz.region.ru/service?wsdl'  # Заменить на реальный WSDL
    client = Client(wsdl=wsdl)
    result = client.service.SendPatientData(patient_data)
    return result
