import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "HEALTHY"
    assert "hostname" in data
    assert "uptime_seconds" in data

def test_liveness_probe(client):
    res = client.get('/health/liveness')
    assert res.status_code == 200
    assert res.get_json()["status"] == "UP"

def test_readiness_probe(client):
    res = client.get('/health/readiness')
    assert res.status_code in [200, 503]
    data = res.get_json()
    assert "status" in data

def test_metrics_endpoint(client):
    res = client.get('/metrics')
    assert res.status_code == 200
    assert b"http_requests_total" in res.data
