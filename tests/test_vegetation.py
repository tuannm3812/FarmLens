from copy import deepcopy
from datetime import date
import pytest
import requests
from conftest import FakeSession
from farmlens.vegetation import VegetationClient, parse_series, combine_samples, sample_dates

POINT=(-32.2569,148.6011)
DATES=['2026-08-28','2026-09-29','2026-10-07']
TODAY=date(2026,10,20)


def series(fixture_json):
    return (parse_series(fixture_json('vegetation_dea.json'),*POINT,DATES),
            parse_series(fixture_json('vegetation_quality_dea.json'),*POINT,DATES))


def test_real_observations_are_joined_to_matching_clear_dry_quality(fixture_json):
    fc,quality=series(fixture_json)
    got=combine_samples(fc,quality,DATES)
    assert got[-1]['date']=='2026-10-07'
    assert got[-1]['green_pct']==33 and got[-1]['dry_pct']==24 and got[-1]['bare_pct']==42
    assert got[-1]['observed_at']=='2026-10-06T23:55:27+00:00'
    assert got[-1]['status']=='available'  # Preserve sum 99; never normalise to 100.


@pytest.mark.parametrize('flags',[{'Cloud':True},{'No water detected':True,'Cloud shadow':True},{'No water detected':1},{},None])
def test_cloud_water_or_missing_quality_cannot_become_cover(fixture_json,flags):
    fc,q=series(fixture_json);q['records'][-1]['bands']['water']=flags
    got=combine_samples(fc,q,DATES)[-1]
    assert got['status']=='excluded' and 'green_pct' not in got


@pytest.mark.parametrize('bad',[255,101,-1,None,True,float('nan')])
def test_invalid_cover_values_are_gaps_not_clipped_percentages(fixture_json,bad):
    fc,q=series(fixture_json);fc['records'][-1]['bands']['photosynthetic_vegetation']=bad
    got=combine_samples(fc,q,DATES)[-1]
    assert got['status']=='excluded' and 'green_pct' not in got


def test_missing_and_mismatched_quality_times_leave_a_gap(fixture_json):
    fc,q=series(fixture_json);q['records'].pop()
    assert combine_samples(fc,q,DATES)[-1]['status']=='excluded'
    q=deepcopy(fc);q['records'][-1]['observed_at']='2026-10-06T23:56:27+00:00'
    assert combine_samples(fc,q,DATES)[-1]['status']=='excluded'


def test_wrong_point_or_unrequested_date_rejects_response(fixture_json):
    p=fixture_json('vegetation_dea.json');p['features'][0]['geometry']['coordinates'][0]+=1
    with pytest.raises(ValueError):parse_series(p,*POINT,DATES)
    with pytest.raises(ValueError):parse_series(fixture_json('vegetation_dea.json'),*POINT,['2026-01-01'])


def test_sample_dates_select_real_recent_monthly_observations_only():
    assert sample_dates(['2024-01-01','2026-09-01','2026-09-29','2026-10-07','2026-11-01'],TODAY)==['2026-09-29','2026-10-07']


def test_client_caches_quality_and_cover_and_isolates_nearby_points(fixture_json,tmp_path):
    session=FakeSession(requests.Timeout(),fixture_json('vegetation_dates_dea.json'),fixture_json('vegetation_dea.json'),fixture_json('vegetation_quality_dea.json'))
    client=VegetationClient(tmp_path,session=session,today=TODAY)
    got=client.fetch(*POINT)
    assert got.status=='live' and got.data['samples'][-1]['green_pct']==33
    params=session.calls[2][1]['params']
    assert params['time']==','.join(DATES) and 'styles' not in params
    assert all('timeout' in call[1] for call in session.calls)
    offline=VegetationClient(tmp_path,cache_only=True,today=TODAY)
    assert offline.fetch(*POINT).status=='cached'
    assert offline.fetch(-32.2579,148.6011).data['samples']==[]
    assert offline.fetch(-32.2579,148.6011).status=='offline'


def test_quality_request_failure_never_returns_unmasked_cover(fixture_json,tmp_path):
    session=FakeSession(fixture_json('vegetation_dates_dea.json'),fixture_json('vegetation_dea.json'),requests.Timeout(),requests.Timeout())
    got=VegetationClient(tmp_path,session=session,today=TODAY).fetch(*POINT)
    assert not any(s['status']=='available' for s in got.data['samples'])
    assert got.status=='offline'


def test_changed_catalogue_keeps_unchanged_cached_observations(fixture_json,tmp_path):
    first=FakeSession(fixture_json('vegetation_dates_dea.json'),fixture_json('vegetation_dea.json'),fixture_json('vegetation_quality_dea.json'))
    VegetationClient(tmp_path,session=first,today=TODAY).fetch(*POINT)
    catalog=fixture_json('vegetation_dates_dea.json')
    catalog['features'][0]['properties']['data_available_for_dates'].append('2026-10-15')
    failed=FakeSession(catalog,*[requests.Timeout() for _ in range(4)])
    got=VegetationClient(tmp_path,session=failed,today=TODAY).fetch(*POINT,refresh=True)
    usable=[s['date'] for s in got.data['samples'] if s['status']=='available']
    assert usable==DATES[:2]
    assert got.data['samples'][-1]['status']=='excluded'
    offline=VegetationClient(tmp_path,cache_only=True,today=TODAY).fetch(*POINT)
    assert [s['date'] for s in offline.data['samples'] if s['status']=='available']==DATES[:2]


def test_date_requests_are_bounded_and_latest_samples_survive_older_timeouts(fixture_json,tmp_path):
    from conftest import FakeResponse
    catalog=fixture_json('vegetation_dates_dea.json')
    catalog['features'][0]['properties']['data_available_for_dates'].insert(0,'2026-07-27')
    class Session:
        def __init__(self): self.calls=[]
        def get(self,url,**kwargs):
            params=kwargs['params'];self.calls.append(params)
            if 'time' not in params:return FakeResponse(catalog)
            dates=params['time'].split(',')
            assert len(dates)<=3
            if dates==['2026-07-27']:raise requests.Timeout()
            name='vegetation_quality_dea.json' if params['layers']=='ga_ls_wo_3' else 'vegetation_dea.json'
            return FakeResponse(fixture_json(name))
    got=VegetationClient(tmp_path,session=Session(),today=TODAY).fetch(*POINT)
    assert got.data['samples'][0]['status']=='excluded'
    assert [s['date'] for s in got.data['samples'] if s['status']=='available']==DATES
