import requests
from django.conf import settings

def get_moscow_egisz_token():
    url = settings.EGISZ_MOSCOW_TOKEN_URL
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.EGISZ_MOSCOW_CLIENT_ID,
        "client_secret": settings.EGISZ_MOSCOW_CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]
