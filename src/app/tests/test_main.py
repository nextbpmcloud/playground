"""Main app tests"""
# from typing import Optional

import functools
import json
import os

from fastapi.testclient import TestClient
from ..main import app


try:
    cached_property
except NameError:
    def cached_property(f):
        """Property with cache"""
        return property(functools.lru_cache()(f))


class AttrDict(dict):
    """A object that handles attribute access on dicts"""
    def __getattr__(self, attr):
        """Delegate attribyte access to dict"""
        try:
            value = self[attr]
            if isinstance(value, dict):
                return AttrDict(value)
            return value
        except KeyError:
            raise AttributeError(f"Object does not have {attr} attribute")


class ResponseWrapper:
    """A small requests.Response wrapper for caching decoded JSON"""

    def __init__(self, response):
        """Create requests.Response response wrapper

        Args:
            response (requests.Response): the requests.response object
        """
        self._response = response

    @cached_property
    def body(self):
        """Decode json and cache"""
        return AttrDict(self.json())

    def __getattr__(self, attr):
        """Delegate everything else to requests.Response objecct"""
        return getattr(self._response, attr)

# class Request(pydantic.BaseModel):
#     method: Optional[str] = 'get'
#     url: str


# class Response(pydantic.BaseModel):
#     code: Optional[int] = 200
#     content_type: Optional[str] = 'application/json'
#     body: Any


# class Sample(pydantic.BaseModel):
#     request: Request
#     response: Response


client = TestClient(app)


def get_sample_filename(sample: str) -> str:
    """Get filename for API examples"""
    return os.path.join(os.path.dirname(__file__), 'api-spec', 'main', 'examples', sample) + '.json'


def get_sample(sample: str) -> dict:
    """Get example data based on API examples"""
    return AttrDict(json.loads(open(get_sample_filename(sample)).read()))


def do_request(sample: dict):
    """Run request based on sample data"""
    request = sample.request
    method = request.get('method', 'get')
    url = request.url
    data = request.get('body')
    return ResponseWrapper(client.request(method, url, data=data))


def check_response(response, sample: dict):
    """Check the response data"""
    return response.status_code == sample['response'].get('code', 200)


def test_home():
    """Test home view"""
    response = client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result['name'] == 'Test API'
    assert result['version'] >= '0.1'


def test_example1():
    """Test with API examples data"""
    sample = get_sample("example1")
    response = do_request(sample)
    assert response.status_code == sample.response.code
    assert response.body.version >= sample.response.body.version
    assert response.body.name == sample.response.body.name
