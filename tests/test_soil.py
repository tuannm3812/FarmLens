import pytest
import requests

from conftest import FakeSession
from farmlens.soil import SoilClient, aggregate_soil


def test_soil_depth_weighting_and_unit_conversions(fixture_json):
    data = aggregate_soil(fixture_json("soil.json"))
    assert data["ph"] == pytest.approx(6.3333333333)
    assert data["clay_pct"] == pytest.approx(23.3333333333)
    # (60% * 5cm + 50% * 10cm + 30% * 15cm) / 30cm.
    assert data["sand_pct"] == pytest.approx(41.6666666667)
    assert data["soc_g_kg"] == pytest.approx(11.6666666667)
    assert data["texture"] == "medium textured"


@pytest.mark.parametrize("damage", ["missing_layer", "missing_depth", "null", "out_of_range"])
def test_missing_or_invalid_soil_not_silently_averaged(fixture_json, damage):
    payload = fixture_json("soil.json")
    layers = payload["properties"]["layers"]
    if damage == "missing_layer":
        layers.pop()
    elif damage == "missing_depth":
        layers[0]["depths"].pop()
    else:
        layers[0]["depths"][0]["values"]["mean"] = None if damage == "null" else 200
    with pytest.raises(ValueError):
        aggregate_soil(payload)


def test_soil_client_requests_three_depths(fixture_json, tmp_path):
    session = FakeSession(fixture_json("soil.json"))
    result = SoilClient(tmp_path, session=session).fetch(-32.26, 148.60)
    assert result.status == "live"
    assert result.data["ph"] == pytest.approx(6.3333333333)
    params = session.calls[0][1]["params"]
    assert params["depth"] == ["0-5cm", "5-15cm", "15-30cm"]
    assert set(params["property"]) == {"phh2o", "clay", "sand", "soc"}
    assert params["value"] == "mean"


def test_soil_failure_returns_labelled_regional_estimate(tmp_path):
    session = FakeSession(requests.Timeout(), requests.Timeout())
    result = SoilClient(tmp_path, session=session).fetch(-31.95, 141.45)
    assert result.status == "offline"
    assert result.data["ph"] == 7.5
    assert "regional" in result.warning.lower()
