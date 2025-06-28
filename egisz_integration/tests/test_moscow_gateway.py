import pytest
from unittest.mock import patch
from egisz_integration import moscow_gateway

def test_send_fhir_resource_success():
    resource_type = 'Patient'
    fhir_json = '{"resourceType": "Patient", "id": "1"}'
    with patch('egisz_integration.moscow_auth.get_moscow_egisz_token', return_value='test-token'):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"result": "ok"}
            mock_post.return_value.raise_for_status = lambda: None
            result = moscow_gateway.send_fhir_resource(resource_type, fhir_json)
            assert result == {"result": "ok"}
