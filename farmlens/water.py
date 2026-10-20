"""Historical water scenarios; never a crop score or irrigation schedule."""
from datetime import date, timedelta
import json
from math import isfinite

from farmlens.api import DataResult
from farmlens.config import ROOT


def water_metadata() -> dict:
    return json.loads((ROOT / 'data' / 'water_profiles.json').read_text())


def _number(value, label, low, high):
    if type(value) not in (int, float) or not isfinite(value) or not low <= value <= high:
        raise ValueError(f'{label} must be a number from {low} to {high}')
    return float(value)


def validate_water_inputs(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError('Expected water scenario inputs')
    meta = water_metadata()
    crop = payload.get('crop_id', 'wheat')
    if not isinstance(crop,str) or crop not in meta['profiles']:
        raise ValueError('Water pilot supports wheat, barley and canola')
    month = payload.get('sowing_month', 5)
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError('Choose a sowing month from January to December')
    stages = payload.get('stages',meta['profiles'][crop]['stages'])
    if not isinstance(stages,list) or len(stages) != 4 or any(type(v) is not int or not 5 <= v <= 180 for v in stages) or not 60 <= sum(stages) <= 300:
        raise ValueError('Enter four growth stages of 5–180 days each, totalling 60–300 days')
    water = payload.get('irrigation','rainfed')
    if water not in ('rainfed','irrigated'):
        raise ValueError('Choose rainfed or irrigation available')
    values = {}
    for key,label,low,high in [('soil_buffer_mm','Soil water buffer (mm)',1,400),
                              ('starting_water_mm','Starting water (mm)',0,400),
                              ('rain_capture_pct','Rain infiltration (%)',0,100),
                              ('efficiency_pct','Irrigation efficiency (%)',10,100)]:
        values[key] = _number(payload.get(key,meta['defaults'][key]),label,low,high)
    if values['starting_water_mm'] > values['soil_buffer_mm']:
        raise ValueError('Starting water cannot exceed the soil water buffer')
    supply = payload.get('supply_ml_ha')
    if supply is not None:
        supply = _number(supply,'Available irrigation (ML/ha)',0,30)
    if water == 'rainfed':
        if supply not in (None,0):
            raise ValueError('Rainfed scenarios cannot include irrigation supply')
        supply = 0.0
    return {'crop_id':crop,'sowing_month':month,'stages':list(stages),'irrigation':water,
            'supply_ml_ha':supply,**values}


def kc_curve(profile: dict, stages: list[int]) -> list[float]:
    initial, mid, end = profile['kc']
    a,b,c,d = stages
    return ([initial]*a + [initial+(mid-initial)*i/b for i in range(1,b+1)]
            + [mid]*c + [mid+(end-mid)*i/d for i in range(1,d+1)])


def daily_balance(rain: list[float], et0: list[float], kc: list[float], inputs: dict) -> dict:
    if not rain or len(rain) != len(et0) or len(rain) != len(kc):
        raise ValueError('Daily balance arrays must have matching nonzero lengths')
    if any(type(v) not in (int,float) or not isfinite(v) or v < 0 for values in (rain,et0,kc) for v in values):
        raise ValueError('Daily balance needs nonnegative finite values')
    store = inputs['starting_water_mm']
    demand_total = retained_total = deficit_total = 0.0
    deficit_days = 0
    for rainfall, reference, coefficient in zip(rain, et0, kc):
        retained = min(inputs['soil_buffer_mm']-store, rainfall*inputs['rain_capture_pct']/100)
        store += retained
        demand = reference*coefficient
        deficit = max(0.0,demand-store)
        store = max(0.0,store-demand)
        demand_total += demand
        retained_total += retained
        deficit_total += deficit
        deficit_days += deficit > 1e-9
    efficiency = inputs['efficiency_pct']/100
    supply = inputs['supply_ml_ha']
    remaining = None if supply is None else max(0.0,deficit_total-supply*100*efficiency)
    return {'demand_mm':demand_total,'rainfall_mm':sum(rain),'rain_retained_mm':retained_total,
            'net_irrigation_mm':deficit_total,'gross_irrigation_ml_ha':deficit_total/efficiency/100,
            'remaining_shortfall_mm':remaining,'ending_storage_mm':store,'deficit_days':deficit_days}


def _quantile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered)-1)*fraction
    lower = int(position)
    upper = min(lower+1,len(ordered)-1)
    return ordered[lower]+(ordered[upper]-ordered[lower])*(position-lower)


def assess_water(source: DataResult, inputs: dict) -> dict:
    inputs = validate_water_inputs(inputs)
    meta = water_metadata()
    profile = meta['profiles'][inputs['crop_id']]
    base = {'status':'unavailable','stale':source.stale,'model_version':meta['version'],
            'inputs':inputs,'profile':profile,'sources':meta['sources'],'seasons':[],
            'summary':None,'season_count':0,'seasons_with_shortfall':None,
            'within_broad_sowing_window':inputs['sowing_month'] in profile['planting_months'],
            'notice':'Historical scenario only; no yield prediction, irrigation schedule or change to crop scores.'}
    if source.status == 'offline':
        return {**base,'reason':'Daily rain and ET0 history unavailable. Refresh data or warm this point’s water cache.'}
    try:
        data = source.data
        first, last = date(data['start_year'],1,1), date(data['end_year'],12,31)
        dates = [(first+timedelta(days=i)).isoformat() for i in range((last-first).days+1)]
        if data['dates'] != dates or any(len(data[key]) != len(dates) for key in ('rain_mm','et0_mm')):
            raise ValueError('Incomplete history')
        if any(type(v) not in (int,float) or not isfinite(v) or v < 0 for key in ('rain_mm','et0_mm') for v in data[key]):
            raise ValueError('Invalid history')
        curve = kc_curve(profile,inputs['stages'])
        starts = [date(year,inputs['sowing_month'],1) for year in range(first.year,last.year+1)]
        starts = [start for start in starts if start+timedelta(days=len(curve)-1) <= last][-10:]
        if len(starts) != 10:
            raise ValueError('Ten complete seasons required')
        seasons = []
        for start in starts:
            offset = (start-first).days
            result = daily_balance(data['rain_mm'][offset:offset+len(curve)],data['et0_mm'][offset:offset+len(curve)],curve,inputs)
            seasons.append({'year':start.year,'start_date':start.isoformat(),
                            'end_date':(start+timedelta(days=len(curve)-1)).isoformat(),**result})
    except (KeyError,TypeError,ValueError,OverflowError):
        return {**base,'reason':'Ten complete, valid historical seasons are required; no partial-season estimate was substituted.'}
    summary = {}
    for key in ('demand_mm','rainfall_mm','rain_retained_mm','net_irrigation_mm','gross_irrigation_ml_ha','remaining_shortfall_mm'):
        values = [season[key] for season in seasons]
        summary[key] = None if any(v is None for v in values) else {
            name:_quantile(values,fraction) for name,fraction in [('p10',.1),('median',.5),('p90',.9)]}
    return {**base,'status':'available','reason':'','seasons':seasons,'summary':summary,'season_count':10,
            'record_period':f'{first.year}–{last.year}',
            'seasons_with_shortfall':None if inputs['supply_ml_ha'] is None else sum(s['remaining_shortfall_mm']>1e-6 for s in seasons)}
