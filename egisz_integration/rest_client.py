import requests

def send_fhir_to_egisz(fhir_json, endpoint_url, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/fhir+json"
    }
    response = requests.post(endpoint_url, data=fhir_json, headers=headers, verify=True)
    return response.status_code, response.text
