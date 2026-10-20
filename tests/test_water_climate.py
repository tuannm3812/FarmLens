from copy import deepcopy
from datetime import date
import json

import pytest
import requests

from conftest import FakeSession
from farmlens.water_climate import WaterClimateClient, parse_water_history


def test_daily_water_history_preserves_dates_units_and_grid(fixture_json):
    got = parse_water_history(fixture_json('water_history.json'), 2015, 2025)
    assert len(got['dates']) == 4018
    assert got['dates'][0] == '2015-01-01'
    assert got['dates'][-1] == '2025-12-31'
    assert got['rain_mm'][0] == 1
    assert got['et0_mm'][0] == 4
    assert got['grid']['longitude'] == 148.5


@pytest.mark.parametrize('damage', ['gap','duplicate','null','negative','boolean','nan','scalar','units','timezone'])
def test_invalid_water_history_is_not_silently_used(fixture_json, damage):
    p = deepcopy(fixture_json('water_history.json'))
    if damage == 'gap':
        for values in p['daily'].values(): values.pop()
    elif damage == 'duplicate': p['daily']['time'][1] = p['daily']['time'][0]
    elif damage == 'scalar': p['daily']['rain_sum'] = 2
    elif damage == 'units': p['daily_units']['rain_sum'] = 'inch'
    elif damage == 'timezone': p['timezone'] = 'UTC'
    else: p['daily']['et0_fao_evapotranspiration'][0] = {'null':None,'negative':-1,'boolean':True,'nan':float('nan')}[damage]
    with pytest.raises(ValueError): parse_water_history(p, 2015, 2025)


def test_client_queries_complete_years_and_reuses_rounded_point_cache(tmp_path, fixture_json):
    session = FakeSession(fixture_json('water_history.json'))
    client = WaterClimateClient(tmp_path, session=session, today=date(2026,10,20))
    first = client.history(-32.2569,148.6011)
    again = client.history(-32.257,148.602)
    assert first.status == 'live' and again.status == 'cached'
    assert first.data == again.data
    assert len(session.calls) == 1
    params = session.calls[0][1]['params']
    assert params['latitude'] == -32.26 and params['longitude'] == 148.60
    assert params['start_date'] == '2015-01-01' and params['end_date'] == '2025-12-31'
    assert params['models'] == 'era5'
    assert params['daily'] == 'rain_sum,et0_fao_evapotranspiration'
    assert session.calls[0][1]['timeout'] == (5,20)


def test_water_retry_recovers_without_regional_defaults(tmp_path, fixture_json):
    session = FakeSession(requests.Timeout(),fixture_json('water_history.json'))
    got = WaterClimateClient(tmp_path,session=session,today=date(2026,1,1)).history(-32.26,148.6)
    assert got.status == 'live' and len(session.calls) == 2


def test_failed_refresh_keeps_valid_stale_cache(tmp_path, fixture_json):
    client = WaterClimateClient(tmp_path,session=FakeSession(fixture_json('water_history.json')),today=date(2026,10,20))
    client.history(-32.26,148.6)
    path = next(tmp_path.glob('*.json'))
    saved = json.loads(path.read_text()); saved['fetched_at'] = '2000-01-01T00:00:00+00:00'
    path.write_text(json.dumps(saved))
    session = FakeSession(requests.Timeout(),requests.ConnectionError())
    result = WaterClimateClient(tmp_path,session=session,today=date(2026,10,20)).history(-32.26,148.6)
    assert result.status == 'cached' and result.stale
    assert result.data['et0_mm'][0] == 4
    assert 'stale' in result.warning and len(session.calls) == 2
    assert json.loads(path.read_text()) == saved


def test_no_water_cache_abstains_and_does_not_request_in_cache_mode(tmp_path):
    session = FakeSession()
    result = WaterClimateClient(tmp_path,session=session,cache_only=True).history(-32.26,148.6)
    assert result.status == 'offline'
    assert result.data['dates'] == [] and result.data['et0_mm'] == []
    assert session.calls == []


def test_network_failure_stops_after_one_retry_and_returns_no_numbers(tmp_path):
    session = FakeSession(requests.Timeout(),requests.Timeout())
    result = WaterClimateClient(tmp_path,session=session).history(-32.26,148.6)
    assert result.status == 'offline' and result.data['rain_mm'] == []
    assert len(session.calls) == 2 and list(tmp_path.iterdir()) == []
