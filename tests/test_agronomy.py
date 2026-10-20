"""Guidance consistency cases, not field-yield validation."""
from dataclasses import replace
import pytest
from farmlens.api import DataResult
from farmlens.scoring import recommend, load_crops


def scenario(rain=1400, *, status='cached', stale=False, irrigation='rainfed', drainage='unknown', ph=6.5):
    climate=DataResult({'annual_temperature_c':20,'annual_rainfall_mm':rain,
                       'coldest_month_min_c':10}, status, 'test climate', stale=stale)
    soil=DataResult({'ph':ph,'clay_pct':20,'sand_pct':60,'soc_g_kg':20},'cached','test PHW')
    return recommend(load_crops(),climate,soil,irrigation=irrigation,drainage=drainage)


@pytest.mark.parametrize('rain,excluded',[(1199,True),(1200,False)])
def test_nsw_macadamia_rainfed_boundary(rain,excluded):
    result=scenario(rain)
    assert ('macadamia' in {c['id'] for c in result['guidance_excluded']}) is excluded
    assert ('macadamia' in {c['id'] for c in result['ranked']}) is not excluded


@pytest.mark.parametrize('rain,excluded',[(300,True),(301,False)])
def test_nsw_lentil_rainfall_boundary(rain,excluded):
    result=scenario(rain)
    assert ('lentil' in {c['id'] for c in result['guidance_excluded']}) is excluded


@pytest.mark.parametrize('status,stale',[('offline',False),('cached',True)])
def test_fallback_or_stale_climate_cannot_decide_local_rain_exclusion(status,stale):
    result=scenario(100,status=status,stale=stale)
    mac=next(c for c in result['ranked'] if c['id']=='macadamia')
    rain=next(c for c in mac['guidance']['checks'] if c['id']=='rainfall')
    assert rain['status']=='not_assessed'
    assert not result['guidance_excluded']


def test_irrigation_does_not_certify_water_supply():
    result=scenario(100,irrigation='irrigated')
    mac=next(c for c in result['ranked'] if c['id']=='macadamia')
    assert mac['subscores']['rainfall']==0
    assert next(c for c in mac['guidance']['checks'] if c['id']=='rainfall')['status']=='not_assessed'
    assert mac['guidance']['validated'] is False


def test_reported_poor_drainage_excludes_sensitive_crops_without_tuning_scores():
    unknown=scenario()
    wet=scenario(drainage='poorly_drained')
    removed={c['id']:c for c in wet['guidance_excluded']}
    assert {'canola','chickpea','lentil','macadamia'} <= removed.keys()
    assert 'barley' in {c['id'] for c in wet['ranked']}  # cultivar-specific tolerance must not be generalised
    prior=next(c for c in unknown['ranked'] if c['id']=='canola')
    assert removed['canola']['total']==prior['total']
    assert all(c['id'] not in removed for c in wet['top_three'])
    assert removed['lentil']['guidance']['checks'][0]['source_url'].startswith('https://')


def test_ph_water_never_satisfies_a_calcium_chloride_test():
    result=scenario(ph=7)
    lentil=next(c for c in result['ranked'] if c['id']=='lentil')
    assert next(c for c in lentil['guidance']['checks'] if c['id']=='ph_method')['status']=='not_assessed'
    assert lentil['guidance']['status']=='needs_checks'
    assert lentil['guidance']['validated'] is False


def test_well_drained_is_user_report_not_validation():
    result=scenario(drainage='well_drained')
    crop=next(c for c in result['ranked'] if c['id']=='lentil')
    assert next(c for c in crop['guidance']['checks'] if c['id']=='drainage')['status']=='met'
    assert crop['guidance']['status']=='needs_checks'
    assert crop['guidance']['validated'] is False


def test_every_crop_has_auditable_guidance_with_remaining_checks():
    result=scenario()
    assert len(result['ranked'])==14  # rice excluded in rainfed mode
    for crop in result['ranked']:
        assert crop['guidance']['checks']
        assert all(c['source_title'] and c['source_url'].startswith('https://') for c in crop['guidance']['checks'])
        assert any(c['status']=='not_assessed' for c in crop['guidance']['checks'])


def test_invalid_drainage_rejected():
    with pytest.raises(ValueError):scenario(drainage='assume good')
