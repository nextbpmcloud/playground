"""Main app tests"""
# from typing import Optional

import pytest

from fastapi.testclient import TestClient
from ..main import app
from ..testutils import get_sample, get_samples, do_request, check_response

client = TestClient(app)


def test_home():
    """Test home view"""
    response = client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result['name'] == 'Test API'
    assert result['version'] >= '0.1'


# ===== Tests gotten from json request / response samples stored in files


def test_home_get():
    """Test API home with sample request/response"""
    sample = get_sample("home_get")
    response = do_request(client, sample)
    check_response(response, sample)


def test_home_get_multi():
    """Test API home with sample requests (multi) / response"""
    sample = get_sample("home_get_multi")
    response = do_request(client, sample)
    check_response(response, sample)


# === Echo Tests using pytest.mark.parametrize

test_data = [
    "hello",
    "hello, this is a test messsage",
    "¡eñeñeñe áéíóú!"
]


@pytest.mark.parametrize("message", test_data)
def test_echo_get(message):
    """Echo get test"""
    response = client.get("/echo", params={"message": message})
    assert response.ok
    assert response.json()['message'] == message


@pytest.mark.parametrize("message", test_data)
def test_echo_post(message):
    """Echo get test"""
    response = client.post("/echo", json={"message": message})
    assert response.ok
    assert response.json()['message'] == message


# === Echo Tests using pytest.mark.parametrize AND loaded from JSON

test_samples = get_samples(['echo_get', 'echo_post'])


@pytest.mark.parametrize("sample", test_samples)
def test_echo_generic(sample):
    """Echo get and post tests with samples loaded from JSON file"""
    response = do_request(client, sample)
    check_response(response, sample)
