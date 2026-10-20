import pytest
import requests

from conftest import FakeSession
from farmlens.australian_soil import AustralianSoilClient, parse_property


def test_real_ph_fixture_depth_weighting_and_units(fixture_json):
    result = parse_property(fixture_json("slga_phw.json"), "PHW")
    assert result["value"] == pytest.approx(6.55)
    assert result["lower"] == pytest.approx(5.25)
    assert result["upper"] == pytest.approx(7.9)
    assert len(result["depths"]) == 3


@pytest.mark.parametrize("bad", ["NoData", None, "nan", "-9999", "15"])
def test_no_data_and_invalid_ph_rejected(fixture_json, bad):
    payload = fixture_json("slga_phw.json")
    payload["results"][0]["attributes"]["Classify.Pixel Value"] = bad
    with pytest.raises(ValueError):
        parse_property(payload, "PHW")


def test_wrong_property_or_missing_depth_rejected(fixture_json):
    payload = fixture_json("slga_phw.json")
    with pytest.raises(ValueError):
        parse_property(payload, "CLY")
    payload["results"] = payload["results"][1:]
    with pytest.raises(ValueError):
        parse_property(payload, "PHW")


def test_uncertainty_optional_and_not_fabricated(fixture_json):
    payload = fixture_json("slga_phw.json")
    payload["results"] = [r for r in payload["results"] if "_EV_" in r["layerName"]]
    result = parse_property(payload, "PHW")
    assert result["value"] == pytest.approx(6.55)
    assert result["lower"] is None and result["upper"] is None


def test_retry_cache_and_fine_coordinate_identity(tmp_path, fixture_json):
    session = FakeSession(requests.Timeout(), fixture_json("slga_phw.json"))
    client = AustralianSoilClient(tmp_path, session=session)
    result = client.fetch_property("PHW", -32.2569, 148.6011)
    assert result.status == "live"
    assert len(session.calls) == 2
    assert session.calls[0][1]["params"]["geometry"] == "148.6011,-32.2569"
    assert session.calls[0][1]["timeout"]
    offline = AustralianSoilClient(tmp_path, cache_only=True)
    assert offline.fetch_property("PHW", -32.2569, 148.6011).status == "cached"
    # Both points round to the same 0.01-degree bucket, but are different soil cells.
    assert offline.fetch_property("PHW", -32.2569, 148.6031).data["value"] is None
    session = FakeSession(requests.Timeout(), requests.Timeout())
    failed = AustralianSoilClient(tmp_path, session=session).fetch_property("PHW", -32.2569, 148.6011, refresh=True)
    assert failed.status == "cached" and "Refresh failed" in failed.warning


def test_no_cache_never_invents_regional_soil(tmp_path):
    result = AustralianSoilClient(tmp_path, cache_only=True).fetch(-32.2569, 148.6011)
    assert result.status == "offline"
    assert result.data["ph"] is None
    assert result.data["clay_pct"] is None
    assert "unavailable" in result.warning.lower()
    assert "regional estimate" not in result.warning.lower()


@pytest.mark.parametrize("code,expected", [("CLY", 23.4555065), ("SND", 65), ("SOC", 13.0166666667)])
def test_real_texture_and_carbon_fixtures(fixture_json, code, expected):
    assert parse_property(fixture_json(f"slga_{code.lower()}.json"), code)["value"] == pytest.approx(expected)
