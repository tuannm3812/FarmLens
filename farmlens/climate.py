"""Open-Meteo history and forecast clients with deterministic aggregation."""
from datetime import date, datetime
from math import isfinite
from zoneinfo import ZoneInfo

import pandas as pd

from farmlens.api import JsonClient, coordinates
from farmlens.config import CACHE_DIR, TIMEZONE, SOURCE_TTLS, regional_defaults

DAILY_FIELDS = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]


def _daily_frame(payload: dict) -> pd.DataFrame:
    try:
        expected_units = {"time": "iso8601", "temperature_2m_max": "°C",
                          "temperature_2m_min": "°C", "precipitation_sum": "mm"}
        if any(payload["daily_units"].get(key) != unit for key, unit in expected_units.items()):
            raise ValueError("Expected daily dates, Celsius temperatures and millimetre rainfall")
        raw = payload["daily"]
        if not all(isinstance(raw[name], list) for name in ["time", *DAILY_FIELDS]):
            raise ValueError("Daily values must be arrays, not scalars")
        frame = pd.DataFrame({name: raw[name] for name in ["time", *DAILY_FIELDS]})
        frame.index = pd.to_datetime(frame.pop("time"), format="%Y-%m-%d")
        frame = frame.apply(pd.to_numeric, errors="raise")
        if frame.empty or frame.index.has_duplicates or frame.index.hasnans:
            raise ValueError("Missing or duplicated dates")
        if not all(isfinite(v) for v in frame.to_numpy().flat):
            raise ValueError("Missing or non-finite daily values")
        if (frame.precipitation_sum < 0).any():
            raise ValueError("Negative rainfall")
        if (frame.temperature_2m_min > frame.temperature_2m_max).any():
            raise ValueError("Minimum temperature exceeds maximum")
        if (frame[DAILY_FIELDS[:2]].abs() > 90).any().any():
            raise ValueError("Invalid temperature units or values")
        frame["mean_temperature"] = (frame.temperature_2m_max + frame.temperature_2m_min) / 2
        return frame.sort_index()
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Malformed daily weather response") from exc


def aggregate_climate(payload: dict, start_year: int, end_year: int) -> dict:
    frame = _daily_frame(payload)
    expected = pd.date_range(f"{start_year}-01-01", f"{end_year}-12-31", freq="D")
    if not frame.index.equals(expected):
        raise ValueError("History does not contain every day of the requested years")
    annual = frame.groupby(frame.index.year)
    monthly_temperature = frame.groupby(frame.index.month).mean()
    coldest = int(monthly_temperature.mean_temperature.idxmin())
    # First sum rainfall per year/month, then average each month across years.
    monthly_rain = frame.precipitation_sum.groupby([frame.index.year, frame.index.month]).sum()
    rain_climatology = monthly_rain.groupby(level=1).mean()
    years = end_year - start_year + 1
    monthly = []
    for month, subset in frame.groupby(frame.index.month):
        monthly.append({"month": int(month),
                        "temperature_c": float(subset.mean_temperature.mean()),
                        "minimum_c": float(subset.temperature_2m_min.mean()),
                        "rainfall_mm": float(rain_climatology.loc[month]),
                        "days": len(subset) / years,
                        "frost_days": float((subset.temperature_2m_min < 0).sum() / years),
                        "hot_days": float((subset.temperature_2m_max >= 35).sum() / years)})
    return {
        "annual_rainfall_mm": float(annual.precipitation_sum.sum().mean()),
        "annual_temperature_c": float(annual.mean_temperature.mean().mean()),
        "coldest_month_min_c": float(monthly_temperature.loc[coldest, "temperature_2m_min"]),
        "driest_three_months_mm": float(rain_climatology.nsmallest(3).sum()),
        "coldest_month": coldest,
        "period": f"{start_year}–{end_year}", "years": end_year - start_year + 1,
        "monthly": monthly,
    }


def aggregate_forecast(payload: dict) -> dict:
    frame = _daily_frame(payload)
    if len(frame) != 7 or not frame.index.equals(pd.date_range(frame.index[0], periods=7)):
        raise ValueError("Expected seven consecutive forecast days")
    rain = float(frame.precipitation_sum.sum())
    low, high = float(frame.temperature_2m_min.min()), float(frame.temperature_2m_max.max())
    codes = payload['daily'].get('weather_code')
    known_codes = {0,1,2,3,45,48,51,53,55,56,57,61,63,65,66,67,71,73,75,77,80,81,82,85,86,95,96,99}
    by_date = {}
    if (payload['daily_units'].get('weather_code') == 'wmo code'
            and isinstance(codes, list) and len(codes) == len(frame)):
        by_date = {day: code if type(code) is int and code in known_codes else None
                   for day, code in zip(payload['daily']['time'], codes)}
    days = [{"date": day.date().isoformat(), "rainfall_mm": float(row.precipitation_sum),
             "min_temperature_c": float(row.temperature_2m_min),
             "max_temperature_c": float(row.temperature_2m_max),
             "weather_code": by_date.get(day.date().isoformat())}
            for day, row in frame.iterrows()]
    return {"rainfall_mm": rain, "min_temperature_c": low, "max_temperature_c": high,
            "days": days,
            "start_date": frame.index[0].date().isoformat(),
            "end_date": frame.index[-1].date().isoformat(),
            "note": f"{rain:.1f} mm rain forecast; temperatures {low:.1f}–{high:.1f}°C."}


def frost_risk(coldest_month_min_c: float) -> str:
    return "high" if coldest_month_min_c <= 2 else "medium" if coldest_month_min_c <= 5 else "low"


class ClimateClient(JsonClient):
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, today: date | None = None, cache_only=False):
        super().__init__(cache_dir, session=session, cache_only=cache_only)
        self._today_override = today

    @property
    def today(self) -> date:
        return self._today_override or datetime.now(ZoneInfo(TIMEZONE)).date()

    def history(self, lat: float, lon: float, *, refresh=False):
        lat, lon = coordinates(lat, lon)
        start, end = self.today.year - 10, self.today.year - 1
        region, defaults = regional_defaults(lat, lon)
        rain, temp, cold, dry = defaults["climate"]
        return self.fetch_json(
            namespace=f"climate_{start}_{end}", source="Open-Meteo history", lat=lat, lon=lon,
            url="https://archive-api.open-meteo.com/v1/archive",
            params={"latitude": lat, "longitude": lon, "start_date": f"{start}-01-01",
                    "end_date": f"{end}-12-31", "daily": ",".join(DAILY_FIELDS),
                    "timezone": TIMEZONE, "models": "era5",
                    "temperature_unit": "celsius", "precipitation_unit": "mm"},
            parse=lambda payload: aggregate_climate(payload, start, end),
            fallback=lambda: {"annual_rainfall_mm": rain, "annual_temperature_c": temp,
                              "coldest_month_min_c": cold, "driest_three_months_mm": dry,
                              "coldest_month": None, "period": "Regional demo estimate",
                              "years": 0, "region": region},
            max_age=SOURCE_TTLS["climate"], refresh=refresh,
        )

    def forecast(self, lat: float, lon: float, *, refresh=False):
        lat, lon = coordinates(lat, lon)
        return self.fetch_json(
            namespace="forecast", source="Open-Meteo forecast", lat=lat, lon=lon,
            url="https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "forecast_days": 7,
                    "daily": ",".join([*DAILY_FIELDS, "weather_code"]), "timezone": TIMEZONE,
                    "temperature_unit": "celsius", "precipitation_unit": "mm"},
            parse=aggregate_forecast,
            fallback=lambda: {"rainfall_mm": None, "min_temperature_c": None,
                              "max_temperature_c": None, "start_date": None, "end_date": None, "days": [],
                              "note": "7-day outlook unavailable. Regional climate estimates are not a forecast."},
            max_age=SOURCE_TTLS["forecast"], refresh=refresh,
            current=lambda data: data["start_date"] == self.today.isoformat(),
        )
