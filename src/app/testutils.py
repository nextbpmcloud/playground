"""Test utilities"""
from typing import Any, List, Optional, Union

import functools
import inspect
import json
import operator
import os

from fastapi.testclient import TestClient

operator_map = {
    '==': operator.eq,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '!=': operator.ne,
    'in': operator.contains
}

try:
    cached_property
except NameError:
    def cached_property(f):
        """Property with cache"""
        return property(functools.lru_cache()(f))


class AttrDict(dict):
    """A object that handles attribute access on dicts"""
    def __getattr__(self, attr: str) -> Any:
        """Delegate attribute access to dict"""
        try:
            value = self[attr]
            if isinstance(value, dict):
                return AttrDict(value)
            if isinstance(value, list):
                return [AttrDict(i) for i in value]  # pragma: no cover
            return value
        except KeyError:
            raise AttributeError(f"Object does not have {attr} attribute")

    def __getitem__(self, key: str) -> Any:
        """Wrap with AttrDict if needed"""
        value = super().__getitem__(key)
        if isinstance(value, dict):
            return AttrDict(value)
        return value

    def item_list(self) -> List:
        """Get dict items and wrap value with AttrDict if needed"""
        return [(key, AttrDict(value) if isinstance(value, dict) else value) for key, value in super().items()]


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

def get_sample_filename(sample: str) -> str:
    """Get filename for API examples"""
    # hack: get caller's caller's filename
    i = 0
    while True:
        frame = inspect.stack()[i]
        if frame.filename != __file__:
            break
        i += 1
    calling_filename = frame.filename
    return os.path.join(os.path.dirname(calling_filename), 'api-spec', 'main', 'examples', sample) + '.json'


def get_sample(sample: str) -> AttrDict:
    """Get example data based on API examples"""
    res = AttrDict(json.loads(open(get_sample_filename(sample)).read()))
    res['name'] = sample
    return res


def get_samples(samples: List[str]) -> List[AttrDict]:
    """Get list of samples"""
    return [get_sample(sample) for sample in samples]


def do_request(client: TestClient, sample: AttrDict) -> Optional[ResponseWrapper]:
    """Run one or more requests based on sample data and return the last response

    Args:
        client: the test client
        sample (dict):

    """
    request: AttrDict
    requests: List[AttrDict]
    try:
        requests = sample.requests
        if not isinstance(requests, list):
            raise ValueError(f"sample.requests must be a list in sample: {sample.name}")  # pragma: no cover
    except AttributeError:
        requests = [sample.request]
    response = None
    for request in requests:
        if not isinstance(request, AttrDict):
            raise TypeError(f"Sample's {sample.name} request must be of type object")  # pragma: no cover
        method = request.get('method', 'get')
        url = request.url
        data = request.get('body')
        response = ResponseWrapper(client.request(method, url, json=data))
    return response


def check_response(response: ResponseWrapper, sample: AttrDict) -> None:
    """Check the response data"""
    expected_response: AttrDict = sample.response
    expected_code: Union[int, List[int]] = expected_response.code
    if not isinstance(expected_code, list):
        expected_code = [expected_code]
    assert response.status_code in expected_code, (
        f"Sample {sample.name}: Unexpected response code. Expected {expected_code}, found: {response.status_code}")
    for key, expected_value in expected_response.body.item_list():
        response_value = getattr(response.body, key)
        op = '=='
        if isinstance(expected_value, AttrDict):
            op = expected_value.get('op', op)
            expected_value = expected_value.value
        if isinstance(expected_value, list) and op == '==':
            op = 'in'       # pragma: no cover
        try:
            opmethod = operator_map[op]
        except KeyError:    # pragma: no cover
            raise ValueError(f"Sample {sample.name}: Unknown operator: {op}")  # pragma: no cover
        assert opmethod(response_value, expected_value), (
            f"Sample {sample.name}: Failed assertion: {key} {op} {repr(expected_value)} . "
            f"Found: {repr(response_value)}")
