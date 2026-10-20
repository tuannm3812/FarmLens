from datetime import date, datetime
import json

import pytest
import requests

from conftest import FakeSession
from farmlens.climate import ClimateClient, aggregate_climate, aggregate_forecast


def test_annual_totals_monthly_climatology_and_leap_years(fixture_json):
    # Each month's rainfall is 10 * month mm; July is 10 C, other days 15 C.
    data = aggregate_climate(fixture_json("history.json"), 2016, 2025)
    assert data["annual_rainfall_mm"] == pytest.approx(780)
    assert data["annual_temperature_c"] == pytest.approx(14.575690545699528)
    assert data["coldest_month_min_c"] == pytest.approx(0)
    assert data["driest_three_months_mm"] == pytest.approx(60)
    assert data["years"] == 10


def test_monthly_summaries_preserve_totals_and_count_extreme_days(fixture_json):
    payload = fixture_json("history.json")
    payload["daily"]["temperature_2m_min"][0] = -1
    payload["daily"]["temperature_2m_max"][0] = 36
    data = aggregate_climate(payload, 2016, 2025)
    assert len(data["monthly"]) == 12
    assert sum(m["rainfall_mm"] for m in data["monthly"]) == pytest.approx(780)
    assert data["monthly"][0]["frost_days"] == pytest.approx(0.1)
    assert data["monthly"][0]["hot_days"] == pytest.approx(0.1)
    assert data["monthly"][1]["days"] == pytest.approx(28.3)


@pytest.mark.parametrize("damage", ["missing_day", "null", "duplicate", "negative_rain"])
def test_incomplete_or_invalid_history_is_rejected(fixture_json, damage):
    payload = fixture_json("history.json")
    if damage == "missing_day":
        for values in payload["daily"].values():
            values.pop()
    elif damage == "null":
        payload["daily"]["precipitation_sum"][0] = None
    elif damage == "duplicate":
        payload["daily"]["time"][0] = payload["daily"]["time"][1]
    else:
        payload["daily"]["precipitation_sum"][0] = -1
    with pytest.raises(ValueError):
        aggregate_climate(payload, 2016, 2025)


def test_forecast_aggregates_seven_days(fixture_json):
    data = aggregate_forecast(fixture_json("forecast.json"))
    assert data["rainfall_mm"] == 12
    assert data["min_temperature_c"] == 6
    assert data["max_temperature_c"] == 28
    assert data["start_date"] == "2026-10-20"
    assert data["end_date"] == "2026-10-26"
    assert len(data['days'])==7
    assert data['days'][0]=={'date':'2026-10-20','rainfall_mm':0.0,'min_temperature_c':6.0,'max_temperature_c':22.0,'weather_code':None}
    assert data['days'][-1]['date']=='2026-10-26'


def test_forecast_optional_weather_codes_do_not_invent_conditions(fixture_json):
    p=fixture_json('forecast.json')
    p['daily']['weather_code']=[0,3,61,95,None,999,True]
    p['daily_units']['weather_code']='wmo code'
    assert [d['weather_code'] for d in aggregate_forecast(p)['days']]==[0,3,61,95,None,None,None]
    p['daily']['weather_code']=[0]
    assert all(d['weather_code'] is None for d in aggregate_forecast(p)['days'])


@pytest.mark.parametrize("fixture", ["forecast.json", "history.json"])
@pytest.mark.parametrize("unit_change", ["temperature", "rainfall", "missing"])
def test_weather_rejects_unexpected_or_missing_units(fixture_json, fixture, unit_change):
    payload = fixture_json(fixture)
    if unit_change == "temperature":
        payload["daily_units"]["temperature_2m_min"] = "°F"
        payload["daily_units"]["temperature_2m_max"] = "°F"
    elif unit_change == "rainfall":
        payload["daily_units"]["precipitation_sum"] = "inch"
    else:
        del payload["daily_units"]
    with pytest.raises(ValueError):
        if fixture == "forecast.json":
            aggregate_forecast(payload)
        else:
            aggregate_climate(payload, 2016, 2025)


def test_history_requests_last_ten_full_years_and_caches(fixture_json, tmp_path):
    session = FakeSession(fixture_json("history.json"))
    client = ClimateClient(tmp_path, session=session, today=date(2026, 10, 20))
    result = client.history(-32.2569, 148.6011)
    assert result.status == "live"
    assert result.data["annual_rainfall_mm"] == pytest.approx(780)
    params = session.calls[0][1]["params"]
    assert params["start_date"] == "2016-01-01"
    assert params["end_date"] == "2025-12-31"
    assert params["timezone"] == "Australia/Sydney"
    # ERA5 supplies precipitation; the live ERA5-Land response has all-null rain.
    assert params["models"] == "era5"
    assert session.calls[0][1]["timeout"] == (5, 20)
    assert "-32.26_148.60" in next(tmp_path.glob("*.json")).name
    again = client.history(-32.2569, 148.6011)
    assert again.status == "cached"
    assert len(session.calls) == 1


def test_forecast_client_uses_saved_fixture(fixture_json, tmp_path):
    session = FakeSession(fixture_json("forecast.json"))
    result = ClimateClient(tmp_path, session=session, today=date(2026, 10, 20)).forecast(-30.30, 153.12)
    assert result.status == "live"
    assert result.data["rainfall_mm"] == 12
    assert session.calls[0][1]["params"]["forecast_days"] == 7


def test_network_failure_retries_once_then_uses_offline_values(tmp_path):
    session = FakeSession(requests.Timeout(), requests.ConnectionError())
    result = ClimateClient(tmp_path, session=session).history(-30.30, 153.12)
    assert result.status == "offline"
    assert result.data["annual_rainfall_mm"] == 1700
    assert "regional" in result.warning.lower()
    assert len(session.calls) == 2
    assert list(tmp_path.glob("*.json")) == []


def test_forecast_fallback_does_not_invent_current_weather(tmp_path):
    session = FakeSession(requests.Timeout(), requests.Timeout())
    result = ClimateClient(tmp_path, session=session).forecast(-31.95, 141.45)
    assert result.status == "offline"
    assert result.data["rainfall_mm"] is None
    assert "unavailable" in result.data["note"].lower()


def test_previous_day_forecast_cache_is_stale_even_inside_ttl(fixture_json, tmp_path):
    first = ClimateClient(tmp_path, session=FakeSession(fixture_json("forecast.json")), today=date(2026, 10, 20))
    first.forecast(-32.26, 148.6)
    session = FakeSession(requests.Timeout(), requests.Timeout())
    result = ClimateClient(tmp_path, session=session, today=date(2026, 10, 21)).forecast(-32.26, 148.6)
    assert result.status == "cached"
    assert result.stale is True
    assert result.data["start_date"] == "2026-10-20"
    assert "stale" in result.warning.lower()
    assert len(session.calls) == 2


def test_failed_forecast_refresh_keeps_existing_cache(fixture_json, tmp_path):
    client = ClimateClient(tmp_path, session=FakeSession(fixture_json("forecast.json")), today=date(2026, 10, 20))
    client.forecast(-32.26, 148.6)
    path = next(tmp_path.glob("*.json"))
    before = json.loads(path.read_text())
    client.session = FakeSession({"daily": None}, {"daily": None})
    result = client.forecast(-32.26, 148.6, refresh=True)
    assert result.status == "cached"
    assert json.loads(path.read_text()) == before


@pytest.mark.parametrize("field", ["temperature_2m_min", "temperature_2m_max", "precipitation_sum"])
def test_scalar_daily_fields_cannot_be_broadcast_into_fake_observations(fixture_json, field):
    payload = fixture_json("forecast.json")
    payload["daily"][field] = 30 if field == "temperature_2m_max" else 1
    with pytest.raises(ValueError):
        aggregate_forecast(payload)


def test_reused_client_checks_forecast_date_after_midnight(fixture_json, tmp_path, monkeypatch):
    class Clock:
        day = 20

        @classmethod
        def now(cls, tz):
            return datetime(2026, 10, cls.day, 12, tzinfo=tz)

    monkeypatch.setattr("farmlens.climate.datetime", Clock)
    tomorrow = fixture_json("forecast.json")
    tomorrow["daily"]["time"] = [f"2026-10-{day}" for day in range(21, 28)]
    session = FakeSession(fixture_json("forecast.json"), tomorrow)
    client = ClimateClient(tmp_path, session=session)
    client.forecast(-32.26, 148.6)
    Clock.day = 21
    result = client.forecast(-32.26, 148.6)
    assert result.status == "live"
    assert result.data["start_date"] == "2026-10-21"
