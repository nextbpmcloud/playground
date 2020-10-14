from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


def test_home():
    """Test home view"""
    response = client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert 'message' in result
    assert result['message'].lower().startswith("hello world")
