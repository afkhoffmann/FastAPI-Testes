from http import HTTPStatus

import pytest
from api_requests.api import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


def test_check_json_format(client):
    response = client.get("/healthcheck")
    assert response.headers["Content-Type"] == "application/json"


def test_integrity(client):
    response = client.get("/healthcheck")
    assert response.json() == {
        "status": "ok"
    }
