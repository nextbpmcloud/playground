"""Main app tests"""
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


def test_home():
    """Test home view"""
    response = client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result['name'] == 'Test API'
    assert result['version'] >= '0.1'
