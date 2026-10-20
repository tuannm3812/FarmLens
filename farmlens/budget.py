"""Editable enterprise gross margins; no yield inference or crop-score changes."""
import json
import math

from farmlens.config import ROOT

LIMITS = {'yield_t_ha':30, 'price_aud_t':10000, 'variable_aud_ha':100000,
          'selling_aud_t':10000, 'irrigation_aud_ha':100000}


def budget_metadata():
    return json.loads((ROOT/'data'/'budget_profiles.json').read_text())


def assess_budget(payload):
    rows = payload.get('rows') if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not 1 <= len(rows) <= 3:
        raise ValueError('Enter one to three crop budgets.')
    profiles = budget_metadata()['profiles']
    result, seen = [], set()
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValueError('Invalid crop budget.')
        crop = raw.get('crop_id')
        if not isinstance(crop, str) or crop not in profiles or crop in seen:
            raise ValueError('Choose wheat, barley or canola once each.')
        seen.add(crop)
        values = {key:raw.get(key) for key in LIMITS}
        for key, value in values.items():
            if value is not None and (type(value) not in (int, float) or
                    not math.isfinite(value) or not 0 <= value <= LIMITS[key]):
                raise ValueError(f'Enter a valid non-negative {key.replace("_", " ")} value.')
        base = {'crop_id':crop, 'name':profiles[crop]['name'], 'inputs':values}
        if any(v is None for v in values.values()):
            result.append({**base, 'status':'incomplete', 'reason':'Enter every assumption; use 0 only when the cost is zero.'})
            continue
        y, p = values['yield_t_ha'], values['price_aud_t']
        per_ha = values['variable_aud_ha'] + values['irrigation_aud_ha']
        per_t = values['selling_aud_t']
        margin = lambda yield_, price: yield_ * (price - per_t) - per_ha
        result.append({**base, 'status':'available', 'revenue_aud_ha':y*p,
            'cost_aud_ha':per_ha+y*per_t, 'margin_aud_ha':margin(y,p),
            'break_even_yield_t_ha':per_ha/(p-per_t) if p>per_t else None,
            'break_even_yield_any':p == per_t and per_ha == 0,
            'break_even_price_aud_t':per_t+per_ha/y if y>0 else None,
            'sensitivity':{'low':margin(y*.8,p*.8), 'base':margin(y,p), 'high':margin(y*1.2,p*1.2)}})
    return {'rows':result, 'currency':'AUD', 'sensitivity_pct':20,
            'notice':'Gross margin before overheads, finance and tax; not net profit. Yield is your assumption, not inferred from suitability.'}
