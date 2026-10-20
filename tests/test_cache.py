import json

import pytest
import requests

from conftest import FakeSession
from farmlens.soil import SoilClient


def test_expired_cache_survives_network_failure(fixture_json, tmp_path):
    first = SoilClient(tmp_path, session=FakeSession(fixture_json("soil.json"))).fetch(-32.26, 148.6)
    path = next(tmp_path.glob("*.json"))
    cached = json.loads(path.read_text())
    cached["fetched_at"] = "2020-01-01T00:00:00+00:00"
    path.write_text(json.dumps(cached))
    session = FakeSession(requests.Timeout(), requests.Timeout())
    result = SoilClient(tmp_path, session=session).fetch(-32.26, 148.6)
    assert result.status == "cached"
    assert result.stale is True
    assert result.data == first.data
    assert len(session.calls) == 2


def test_malformed_response_retried_without_caching(tmp_path):
    session = FakeSession({"properties": None}, {"error": "unavailable"})
    result = SoilClient(tmp_path, session=session).fetch(-32.26, 148.6)
    assert result.status == "offline"
    assert len(session.calls) == 2
    assert not list(tmp_path.glob("*.json"))


def test_invalid_cache_ignored_and_refetched(fixture_json, tmp_path):
    client = SoilClient(tmp_path, session=FakeSession(fixture_json("soil.json")))
    client.fetch(-32.26, 148.6)
    next(tmp_path.glob("*.json")).write_text("{broken json")
    client = SoilClient(tmp_path, session=FakeSession(fixture_json("soil.json")))
    assert client.fetch(-32.26, 148.6).status == "live"


def test_cache_write_failure_does_not_discard_live_data(fixture_json, tmp_path):
    not_a_directory = tmp_path / "file"
    not_a_directory.write_text("occupied")
    result = SoilClient(not_a_directory, session=FakeSession(fixture_json("soil.json"))).fetch(-32.26, 148.6)
    assert result.status == "live"
    assert result.data["ph"] == pytest.approx(6.3333333333)
    assert "cache" in result.warning.lower()


@pytest.mark.parametrize("error", [requests.HTTPError("503"), requests.Timeout(), ValueError("invalid JSON")])
def test_retry_can_recover_with_live_payload(fixture_json, tmp_path, error):
    session = FakeSession(error, fixture_json("soil.json"))
    result = SoilClient(tmp_path, session=session).fetch(-32.26, 148.6)
    assert result.status == "live"
    assert result.data["ph"] == pytest.approx(6.3333333333)
    assert len(session.calls) == 2
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_cache_only_mode_never_requests_network(fixture_json, tmp_path):
    session = FakeSession()
    result = SoilClient(tmp_path, session=session, cache_only=True).fetch(-32.26, 148.6)
    assert result.status == "offline"
    assert session.calls == []
    SoilClient(tmp_path, session=FakeSession(fixture_json("soil.json"))).fetch(-32.26, 148.6)
    result = SoilClient(tmp_path, session=session, cache_only=True).fetch(-32.26, 148.6)
    assert result.status == "cached"
    assert result.data["ph"] == pytest.approx(6.3333333333)
    assert session.calls == []
