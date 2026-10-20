from dataclasses import replace
import math

import pytest

from farmlens.api import DataResult
from farmlens.scoring import load_crops, range_score, score_crop, recommend, season_context


@pytest.fixture
def crop():
    return next(c for c in load_crops() if c["id"] == "wheat")


@pytest.fixture
def climate():
    monthly = [{"month": month, "temperature_c": 18, "minimum_c": 5,
                "rainfall_mm": 50, "days": 30, "frost_days": 1, "hot_days": 2}
               for month in range(1, 13)]
    return DataResult({"annual_temperature_c": 18, "annual_rainfall_mm": 800,
                       "coldest_month_min_c": 5, "monthly": monthly}, "cached", "test history")


@pytest.fixture
def soil():
    return DataResult({"ph": 6.5}, "live", "test soil")


@pytest.mark.parametrize("ph", [None, float("nan"), -1, 15])
def test_missing_or_invalid_soil_abstains(climate, ph):
    soil = DataResult({"ph": ph}, "offline", "Australian SLGA")
    result = recommend(load_crops(), climate, soil)
    assert result["top_three"] == []
    assert not result["has_strong_match"]
    assert any("Soil pH" in warning for warning in result["warnings"])


@pytest.mark.parametrize("value,want", [(0,0),(5,0),(10,50),(15,100),(20,100),(25,100),(30,50),(35,0),(40,0)])
def test_range_linear_interpolation_and_absolute_boundaries(value, want):
    assert range_score(value, 5, 15, 25, 35) == want


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_values_rejected(value):
    with pytest.raises(ValueError):
        range_score(value, 5, 15, 25, 35)


def test_inverted_range_rejected():
    with pytest.raises(ValueError):
        range_score(10, 5, 25, 15, 35)


def test_in_range_crop_scores_high(crop):
    result = score_crop(crop, temperature_c=18, rainfall_mm=800, ph=6.5, frost_min_c=5, fire_exposure="low")
    assert result["total"] == 100
    assert all(value == 100 for value in result["subscores"].values() if value is not None)


def test_out_of_range_crop_is_low_and_zero_caps_total(crop):
    result = score_crop(crop, temperature_c=18, rainfall_mm=50, ph=6.5, frost_min_c=5, fire_exposure="low")
    assert result["subscores"]["rainfall"] == 0
    assert result["uncapped_total"] == pytest.approx(70)
    assert result["total"] == 20
    assert result["weakest_factor"] == "rainfall"
    assert result["zero_capped"] is True


def test_missing_fire_does_not_become_perfect_fire_score(crop):
    result = score_crop(crop, temperature_c=18, rainfall_mm=525, ph=6.5, frost_min_c=5)
    assert result["subscores"]["fire"] is None
    assert result["total"] == pytest.approx(83.3333333333)
    assert result["assessed_weight_pct"] == pytest.approx(72)


def test_high_fire_applies_zero_cap(crop):
    result = score_crop(crop, temperature_c=18, rainfall_mm=800, ph=6.5, frost_min_c=5, fire_exposure="high")
    assert result["subscores"]["fire"] == 0
    assert result["total"] == 20


@pytest.mark.parametrize("magnitude", [1e307, 1e308])
def test_large_finite_weights_preserve_scores_and_evidence_coverage(crop, magnitude):
    weights = {key: magnitude for key in ("temperature", "rainfall", "ph", "frost", "fire")}
    result = score_crop(crop, temperature_c=18, rainfall_mm=525, ph=6.5, frost_min_c=5, weights=weights)
    assert result["total"] == pytest.approx(87.5)
    assert result["assessed_weight_pct"] == pytest.approx(80)


@pytest.mark.parametrize("weights", [{}, {"temperature": 1}, {"temperature": -1, "rainfall": 1, "ph": 1, "frost": 1, "fire": 1}])
def test_invalid_weights_rejected(crop, weights):
    with pytest.raises(ValueError):
        score_crop(crop, temperature_c=18, rainfall_mm=800, ph=6.5, frost_min_c=5, weights=weights)


def test_all_profiles_are_sourced_and_valid():
    crops = load_crops()
    assert len(crops) == 15
    assert len({c["id"] for c in crops}) == 15
    for crop in crops:
        assert crop["source_url"].endswith("id=" + str(crop["ecocrop_id"]))
        assert crop["category"] in {"annual", "pasture", "perennial"}


def test_season_context_wraps_year_and_preserves_rain_units(climate):
    result = season_context(climate.data, 11, 5)
    assert result["months"] == [11,12,1,2,3]
    assert result["temperature_c"] == 18
    assert result["rainfall_mm"] == 250
    assert result["frost_days"] == 5


def test_monthly_temperatures_are_day_weighted(climate):
    climate.data["monthly"][0].update(temperature_c=10, days=31)
    climate.data["monthly"][1].update(temperature_c=20, days=28)
    assert season_context(climate.data, 1, 2)["temperature_c"] == pytest.approx(870/59)


def test_seasonal_mode_filters_month_and_perennials(climate, soil):
    result = recommend(load_crops(), climate, soil, mode="season", planting_month=10)
    assert {r["id"] for r in result["ranked"]} == {"sorghum", "cotton"}
    assert all(r["category"] == "annual" for r in result["ranked"])
    assert "rice" in result["excluded"]
    assert len(result["top_three"]) == 2


def test_irrigation_does_not_invent_extra_rain_or_remove_deficit_cap(climate, soil):
    climate.data["annual_rainfall_mm"] = 100
    result = recommend(load_crops(), climate, soil, mode="season", planting_month=10, irrigation="irrigated")
    assert "rice" in {r["id"] for r in result["ranked"]}
    assert all(r["subscores"]["rainfall"] == 0 for r in result["ranked"])
    assert all(r["total"] <= 20 for r in result["ranked"])
    assert "water budget" in " ".join(result["warnings"]).lower()


def test_no_strong_match_when_all_crops_hit_rainfall_limits(climate, soil):
    climate.data["annual_rainfall_mm"] = 100
    result = recommend(load_crops(), climate, soil)
    assert result["has_strong_match"] is False
    assert len(result["top_three"]) == 3
    assert all(not r["strong_match"] for r in result["top_three"])


def test_offline_soil_marks_rankings_as_provisional(climate, soil):
    result = recommend(load_crops(), climate, replace(soil, status="offline"))
    assert result["evidence_quality"] == "provisional — offline inputs"
    assert "soil" in " ".join(result["warnings"]).lower()


def test_stale_source_is_disclosed(climate, soil):
    result = recommend(load_crops(), replace(climate, stale=True), soil)
    assert "stale" in result["evidence_quality"]


def test_seasonal_mode_abstains_without_monthly_history(climate, soil):
    del climate.data["monthly"]
    result = recommend(load_crops(), climate, soil, mode="season", planting_month=5)
    assert result["top_three"] == []
    assert "monthly" in " ".join(result["warnings"]).lower()


def test_category_filter_and_stable_ties(climate, soil):
    crops = load_crops()
    a = recommend(crops, climate, soil, category="perennial")
    b = recommend(list(reversed(crops)), climate, soil, category="perennial")
    assert all(r["category"] == "perennial" for r in a["ranked"])
    assert [r["id"] for r in a["ranked"]] == [r["id"] for r in b["ranked"]]


@pytest.mark.parametrize("kwargs", [{"mode":"wrong"},{"mode":"season"},{"mode":"season","planting_month":13},{"category":"trees"},{"irrigation":"yes"}])
def test_invalid_scenarios_rejected(climate, soil, kwargs):
    with pytest.raises(ValueError):
        recommend(load_crops(), climate, soil, **kwargs)
