from datetime import date
from dataclasses import replace

import pytest

from farmlens.api import DataResult
from farmlens.water_climate import parse_water_history
from farmlens.water import validate_water_inputs, water_metadata, kc_curve, daily_balance, assess_water


def inputs(**overrides):
    return validate_water_inputs({'crop_id':'wheat','sowing_month':5,'stages':[20,30,60,40],
        'soil_buffer_mm':100,'starting_water_mm':50,'rain_capture_pct':80,'efficiency_pct':80,
        'irrigation':'rainfed','supply_ml_ha':None,**overrides})


def test_hand_calculated_balance_preserves_timing_and_overflow():
    # Day 1: 10-mm demand, empty store => 10 deficit.
    # Day 2: 100 rain capped at 20 storage, consume 10; end 10.
    # Day 3: 10 demand uses remainder. Total rain cannot erase day 1 deficit.
    got = daily_balance([0,100,0],[10,10,10],[1,1,1],inputs(
        soil_buffer_mm=20,starting_water_mm=0,rain_capture_pct=100,efficiency_pct=50))
    assert got['demand_mm'] == 30
    assert got['rainfall_mm'] == 100
    assert got['rain_retained_mm'] == 20
    assert got['net_irrigation_mm'] == 10
    assert got['gross_irrigation_ml_ha'] == .2
    assert got['remaining_shortfall_mm'] == 10
    assert got['ending_storage_mm'] == 0
    assert got['deficit_days'] == 1


def test_infiltration_and_starting_water_are_used_once():
    got = daily_balance([10,0],[10,10],[1,1],inputs(starting_water_mm=5,rain_capture_pct=50))
    assert got['rain_retained_mm'] == 5
    assert got['net_irrigation_mm'] == 10
    assert got['ending_storage_mm'] == 0


def test_unknown_irrigation_supply_is_distinct_from_zero_and_converts_ml_ha():
    unknown = daily_balance([0],[100],[1],inputs(starting_water_mm=0,irrigation='irrigated'))
    zero = daily_balance([0],[100],[1],inputs(starting_water_mm=0,irrigation='irrigated',supply_ml_ha=0))
    supplied = daily_balance([0],[100],[1],inputs(starting_water_mm=0,irrigation='irrigated',supply_ml_ha=.5))
    covered = daily_balance([0],[100],[1],inputs(starting_water_mm=0,irrigation='irrigated',supply_ml_ha=10))
    assert unknown['remaining_shortfall_mm'] is None
    assert zero['remaining_shortfall_mm'] == 100
    assert supplied['remaining_shortfall_mm'] == 60  # .5 ML/ha = 50 mm gross × 80%
    assert covered['remaining_shortfall_mm'] == 0
    assert unknown['gross_irrigation_ml_ha'] == 1.25


@pytest.mark.parametrize('change',[
    {'crop_id':'rice'},{'sowing_month':13},{'sowing_month':True},{'soil_buffer_mm':0},
    {'starting_water_mm':101},{'starting_water_mm':-1},{'efficiency_pct':0},
    {'efficiency_pct':101},{'rain_capture_pct':float('nan')},{'supply_ml_ha':True},
    {'stages':[1,2,3,4]},{'stages':[20,30,60]},{'stages':[20,30,60,40.5]},
    {'irrigation':'sometimes'},{'supply_ml_ha':-1},{'soil_buffer_mm':'100'},
])
def test_invalid_assumptions_fail_without_coercing_values(change):
    with pytest.raises(ValueError): inputs(**change)


def test_rainfed_mode_cannot_silently_use_irrigation_supply():
    with pytest.raises(ValueError): inputs(supply_ml_ha=2)
    assert inputs()['supply_ml_ha'] == 0


def test_stage_curve_has_correct_endpoints_and_length():
    profile = water_metadata()['profiles']['wheat']
    curve = kc_curve(profile,[2,2,2,2])
    assert curve == pytest.approx([.3,.3,.725,1.15,1.15,1.15,.7,.25])
    canola = kc_curve(water_metadata()['profiles']['canola'],[1,1,1,1])
    assert canola == pytest.approx([.35,1.1,1.1,.35])


def test_ten_complete_seasons_and_leap_day_are_counted(fixture_json):
    source = DataResult(parse_water_history(fixture_json('water_history.json'),2015,2025),'cached','test')
    got = assess_water(source,inputs(sowing_month=2))
    assert got['status'] == 'available' and got['season_count'] == 10
    assert got['seasons'][0]['start_date'] == '2016-02-01'
    assert got['seasons'][-1]['start_date'] == '2025-02-01'
    assert got['seasons'][0]['end_date'] == '2016-06-29'
    assert got['seasons'][-1]['end_date'] == '2025-06-30'
    # Constant 4 mm ET0; sum(Kc) = 6 + 22.175 + 69 + 27.55 = 124.725.
    assert got['summary']['demand_mm']['median'] == pytest.approx(498.9)
    assert all(row['rainfall_mm'] == 150 for row in got['seasons'])
    assert got['within_broad_sowing_window'] is False


def test_cross_year_seasons_exclude_incomplete_last_year(fixture_json):
    source = DataResult(parse_water_history(fixture_json('water_history.json'),2015,2025),'cached','test')
    got = assess_water(source,inputs(sowing_month=11))
    assert got['seasons'][0]['start_date'] == '2015-11-01'
    assert got['seasons'][-1]['start_date'] == '2024-11-01'
    assert got['seasons'][-1]['end_date'] == '2025-03-30'
    assert got['season_count'] == 10


def test_offline_and_incomplete_history_abstain_but_stale_is_explicit(fixture_json):
    source = DataResult(parse_water_history(fixture_json('water_history.json'),2015,2025),'cached','test')
    stale = assess_water(replace(source,stale=True),inputs())
    assert stale['stale'] is True and stale['status'] == 'available'
    offline = assess_water(replace(source,status='offline'),inputs())
    assert offline['status'] == 'unavailable' and offline['summary'] is None
    # Even an internal damaged data object cannot silently drop a year or a day.
    data = {**source.data,'dates':source.data['dates'][:-1]}
    broken = assess_water(replace(source,data=data),inputs())
    assert broken['status'] == 'unavailable' and broken['seasons'] == []


def test_historical_ranges_are_computed_per_season_not_from_average_weather(fixture_json):
    data = parse_water_history(fixture_json('water_history.json'),2015,2025)
    data['rain_mm'] = [1000 if d[:4] in ('2016','2017','2018','2019','2020') else 0 for d in data['dates']]
    got = assess_water(DataResult(data,'cached','test'),inputs(starting_water_mm=0,rain_capture_pct=100))
    assert got['summary']['net_irrigation_mm']['p10'] == 0
    assert got['summary']['net_irrigation_mm']['p90'] == pytest.approx(498.9)
    assert got['seasons_with_shortfall'] == 5
