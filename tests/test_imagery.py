"""NSW survey metadata, never fabricated capture dates."""
from copy import deepcopy

import pytest
import requests

from conftest import FakeSession
from farmlens.imagery import ImageryClient, parse_metadata

POINT = (-32.2569, 148.6011)


def test_real_dubbo_metadata_and_precise_cache(fixture_json, tmp_path):
    session = FakeSession(fixture_json("nsw_imagery_dates.json"))
    client = ImageryClient(tmp_path, session=session)
    result = client.fetch(*POINT)
    assert result.status == "live"
    assert result.data["blocks"] == [
        {"name": "DUBBO", "survey_date": "2009-04-03", "resolution_cm": 10}
    ]
    assert result.data["point"] == {"lat": POINT[0], "lon": POINT[1]}
    params = session.calls[0][1]["params"]
    assert params["geometry"] == "148.6011,-32.2569"
    assert params["inSR"] == 4326 and params["returnGeometry"] == "false"
    assert client.fetch(*POINT).status == "cached"
    assert len(session.calls) == 1
    assert "-32.25690_148.60110" in next(tmp_path.glob("*.json")).name
    assert ImageryClient(tmp_path, cache_only=True).fetch(-32.257, 148.6011).status == "offline"


def test_no_date_is_not_an_invented_capture(fixture_json):
    payload = fixture_json("nsw_imagery_dates.json")
    payload["features"][0]["attributes"]["BlockStartDate"] = None
    assert parse_metadata(payload, *POINT)["blocks"][0]["survey_date"] is None
    assert parse_metadata({"features": []}, *POINT)["blocks"] == []


@pytest.mark.parametrize("damage", ["error", "boolean_date", "huge_date", "resolution", "shape"])
def test_invalid_metadata_falls_back_without_estimate(fixture_json, tmp_path, damage):
    payload = deepcopy(fixture_json("nsw_imagery_dates.json"))
    attrs = payload["features"][0]["attributes"]
    if damage == "error":
        payload = {"error": {"message": "Unavailable"}}
    if damage == "boolean_date":
        attrs["BlockStartDate"] = True
    if damage == "huge_date":
        attrs["BlockStartDate"] = 1e30
    if damage == "resolution":
        attrs["Resolution_cm"] = -1
    if damage == "shape":
        payload["features"] = {}
    result = ImageryClient(tmp_path, session=FakeSession(payload, payload)).fetch(*POINT)
    assert result.status == "offline" and result.data["blocks"] == []


def test_retry_then_cached_fallback_and_invalid_location(fixture_json, tmp_path):
    client = ImageryClient(
        tmp_path,
        session=FakeSession(requests.Timeout(), fixture_json("nsw_imagery_dates.json")),
    )
    assert client.fetch(*POINT).status == "live"
    assert len(client.session.calls) == 2
    client.session = FakeSession(requests.Timeout(), requests.Timeout())
    assert client.fetch(*POINT, refresh=True).status == "cached"
    with pytest.raises(ValueError):
        client.fetch(-35.28, 149.13)
