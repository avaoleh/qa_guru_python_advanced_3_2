import pytest
import requests
from http import HTTPStatus
from app.models.User import *
from app.models.AppStatus import AppStatus
from fastapi_pagination import Page

@pytest.mark.smoke
class TestSmoke:


    def test_status_healthcheck(self, app_url: str):
        response = requests.get(f"{app_url}/status/")
        assert response.status_code == HTTPStatus.OK
        result = response.json()
        AppStatus.model_validate(result)
        assert result["database"]
        assert result['status']

    def test_api_endpoints(self, app_url: str):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK

        result = response.json()
        Page[User].model_validate(result)

        assert 'items' in result
        assert len(result['items']) > 0
