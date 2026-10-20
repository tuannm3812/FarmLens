"""NSW guidance checks, independent of uncalibrated proxy-score arithmetic.

A compatible conflict withholds a candidate; unknowns never become passes.
Published pHCa limits are not evaluated against SLGA pH-water values.
"""
import json
from pathlib import Path
from farmlens.config import ROOT
from farmlens.soil_factors import valid

DRAINAGE_OPTIONS = ('unknown', 'well_drained', 'poorly_drained')
GUIDANCE_PATH = ROOT / 'data' / 'nsw_guidance.json'


def load_guidance(path=GUIDANCE_PATH):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def assess_guidance(crop_id, climate, *, irrigation, drainage='unknown', catalogue=None):
    if drainage not in DRAINAGE_OPTIONS:
        raise ValueError('Choose unknown, well-drained or poorly drained soil')
    catalogue = load_guidance() if catalogue is None else catalogue
    profile = catalogue['profiles'].get(crop_id)
    if profile is None:
        return {'status':'needs_checks', 'validated':False,
                'summary':'No NSW guidance profile reviewed for this crop.', 'checks':[]}
    checks = []

    def add(check_id, status, message):
        checks.append({'id':check_id, 'status':status, 'message':message,
                       'source_title':profile['source_title'], 'source_url':profile['source_url']})

    for check in profile['checks']:
        add(check['id'], 'not_assessed', check['message'])
    if profile.get('avoid_poor_drainage'):
        if drainage == 'poorly_drained':
            add('drainage','conflict','Reported poor drainage conflicts with this crop’s site guidance; resolve waterlogging risk before shortlisting.')
        elif drainage == 'well_drained':
            add('drainage','met','Well-drained soil reported by you; this has not been measured or inferred from texture.')
        else:
            add('drainage','not_assessed','Confirm drainage and waterlogging history; sand and clay percentages cannot establish drainage.')
    if 'rainfed_min_mm' in profile:
        threshold = profile['rainfed_min_mm']
        inclusive = profile['rainfed_min_inclusive']
        requirement = f"{'at least' if inclusive else 'more than'} {threshold:,.0f} mm/year"
        rain = valid(climate.data.get('annual_rainfall_mm'), 100000)
        if irrigation == 'irrigated':
            add('rainfall','not_assessed',f'Rainfed guidance uses {requirement}; irrigation supply, water quality and seasonal water budget remain unverified.')
        elif climate.status not in ('cached','live') or climate.stale or rain is None:
            add('rainfall','not_assessed',f'Rainfed guidance uses {requirement}; fallback, stale or missing rainfall cannot decide this check.')
        else:
            meets = rain >= threshold if inclusive else rain > threshold
            add('rainfall','met' if meets else 'conflict',
                f'Historical mean {rain:,.0f} mm/year {"meets" if meets else "does not meet"} the {requirement} rainfed screen; seasonal water availability still needs checking.')
    conflict = any(c['status']=='conflict' for c in checks)
    return {'status':'conflict' if conflict else 'needs_checks', 'validated':False,
            'summary':'Withheld: a known input conflicts with NSW guidance.' if conflict else 'Local checks required; guidance consistency is not field validation.',
            'checks':checks}
