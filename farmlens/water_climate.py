"""Separate daily rain/ET0 history for the optional water scenario."""
from datetime import date, datetime, timedelta
from math import isfinite
from zoneinfo import ZoneInfo

from farmlens.api import JsonClient, coordinates
from farmlens.config import CACHE_DIR, TIMEZONE, SOURCE_TTLS

FIELDS = ('rain_sum', 'et0_fao_evapotranspiration')


def parse_water_history(payload: dict, start_year: int, end_year: int) -> dict:
    try:
        units = payload['daily_units']
        if payload['timezone'] != TIMEZONE or units.get('time') != 'iso8601' or any(units.get(k) != 'mm' for k in FIELDS):
            raise ValueError('Water history requires local daily dates and millimetres')
        raw = payload['daily']
        start, end = date(start_year, 1, 1), date(end_year, 12, 31)
        expected = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
        if raw['time'] != expected:
            raise ValueError('Incomplete or unordered daily water history')
        for key in FIELDS:
            values = raw[key]
            if not isinstance(values, list) or len(values) != len(expected):
                raise ValueError('Daily water values must cover every requested day')
            if any(type(v) not in (int, float) or not isfinite(v) or v < 0 for v in values):
                raise ValueError('Missing or invalid daily rain/ET0')
        grid = {key: payload.get(key) for key in ('latitude','longitude','elevation')}
        if any(type(v) not in (int,float) or not isfinite(v) for v in grid.values()):
            raise ValueError('Missing weather grid metadata')
        if not -90 <= grid['latitude'] <= 90 or not -180 <= grid['longitude'] <= 180:
            raise ValueError('Invalid weather grid coordinates')
        return {'dates': raw['time'], 'rain_mm': raw['rain_sum'], 'et0_mm': raw['et0_fao_evapotranspiration'],
                'start_year': start_year, 'end_year': end_year, 'grid': grid}
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('Malformed daily water history') from exc


class WaterClimateClient(JsonClient):
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, today: date | None = None, cache_only=False):
        super().__init__(cache_dir, session=session, cache_only=cache_only)
        self.today = today or datetime.now(ZoneInfo(TIMEZONE)).date()

    def history(self, lat: float, lon: float, *, refresh=False):
        lat, lon = coordinates(lat, lon)
        # An extra calendar year supplies complete seasons that cross New Year.
        start, end = self.today.year - 11, self.today.year - 1
        return self.fetch_json(
            namespace=f'water_era5_{start}_{end}', source='Open-Meteo ERA5 rain and FAO-56 ET0',
            lat=lat, lon=lon, url='https://archive-api.open-meteo.com/v1/archive',
            params={'latitude':lat, 'longitude':lon, 'start_date':f'{start}-01-01', 'end_date':f'{end}-12-31',
                    'daily':','.join(FIELDS), 'timezone':TIMEZONE, 'models':'era5', 'precipitation_unit':'mm'},
            parse=lambda p: parse_water_history(p,start,end),
            fallback=lambda: {'dates':[], 'rain_mm':[], 'et0_mm':[], 'start_year':start, 'end_year':end, 'grid':None},
            max_age=SOURCE_TTLS['climate'], refresh=refresh,
            fallback_note='water assessment unavailable; no estimated ET0 substituted',
        )
