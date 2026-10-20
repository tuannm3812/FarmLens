import json
from pathlib import Path

import pytest
import requests


@pytest.fixture(autouse=True)
def no_live_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Tests must not make live network requests")
    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    monkeypatch.setattr("farmlens.soil._rate_limit", lambda: None)


@pytest.fixture
def fixture_json():
    def read(name):
        return json.loads((Path(__file__).parent / "fixtures" / name).read_text())
    return read


class FakeSession:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        item = next(self.responses)
        if isinstance(item, Exception):
            raise item
        return FakeResponse(item)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload
