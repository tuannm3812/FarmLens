"""Sampled DEA fractional cover, gated by matching clear/dry water observations."""
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
import time
from zoneinfo import ZoneInfo

from farmlens.api import JsonClient, DataResult, coordinates
from farmlens.config import CACHE_DIR, TIMEZONE
from farmlens.location import in_nsw

SOURCE = 'DEA Fractional Cover + Water Observations (Geoscience Australia)'
SOURCE_URL = 'https://knowledge.dea.ga.gov.au/data/product/dea-fractional-cover-landsat/'
METHOD_URL = 'https://knowledge.dea.ga.gov.au/notebooks/DEA_products/DEA_Fractional_Cover/'


def feature_properties(payload, lat, lon):
    if payload.get('type') != 'FeatureCollection' or not isinstance(payload.get('features'), list):
        raise ValueError('Expected DEA feature collection')
    if not payload['features']:
        return {}
    if len(payload['features']) != 1:
        raise ValueError('Expected one point')
    f = payload['features'][0]
    geometry = f['geometry']
    point = geometry['coordinates']
    if geometry['type'] != 'Point' or len(point) != 2 or any(
        type(v) not in (int, float) or not math.isfinite(v) or abs(v-e)>.00002
        for v,e in zip(point,(lon,lat))):
        raise ValueError('DEA returned a different point')
    return f['properties']


def sample_dates(dates, today):
    """At most one actual scene per month, latest twelve months within one year."""
    if not isinstance(dates, list):
        raise ValueError('Invalid available dates')
    by_month = {}
    for value in sorted(set(dates)):
        d = date.fromisoformat(value)
        if today-timedelta(days=365) <= d <= today:
            by_month[value[:7]] = value
    return sorted(by_month.values())[-12:]


def parse_series(payload, lat, lon, requested, *, cached_subset=False):
    props = feature_properties(payload, lat, lon)
    records = props.get('data', [])
    if not isinstance(records, list):
        raise ValueError('Invalid DEA observations')
    parsed, seen = [], set()
    for row in records:
        observed = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
        # DEA groups Landsat observations by local solar day, not UTC date.
        day = (observed+timedelta(hours=lon/15)).date().isoformat()
        if cached_subset and day not in requested:
            continue
        if day not in requested or day in seen or not isinstance(row['bands'], dict):
            raise ValueError('Unexpected or duplicate observation date')
        seen.add(day)
        parsed.append({'date':day, 'observed_at':observed.isoformat(), 'bands':row['bands']})
    return {'records':parsed}


def combine_samples(cover, quality, dates):
    values = {r['date']:r for r in cover['records']}
    masks = {r['date']:r for r in quality['records']}
    output = []
    for day in dates:
        row, mask = values.get(day), masks.get(day)
        base = {'date':day, 'status':'excluded'}
        if not row:
            output.append({**base, 'reason':'No cover observation'}); continue
        bands = row['bands']
        water = mask['bands'].get('water') if mask else None
        # The WMS JSON encodes WOfS dry/clear (all flags unset) with this exact boolean label.
        clear = isinstance(water,dict) and set(water)=={'No water detected'} and water['No water detected'] is True
        if not mask or mask['observed_at'] != row['observed_at'] or not clear:
            output.append({**base, 'reason':'Water, cloud, shadow or missing quality flag'}); continue
        names = {'green_pct':'photosynthetic_vegetation','dry_pct':'non_photosynthetic_vegetation','bare_pct':'bare_soil'}
        fractions = {key:bands.get(name) for key,name in names.items()}
        ue = bands.get('ue')
        if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=100 for v in fractions.values()) or type(ue) not in (int,float) or not math.isfinite(ue) or not 0<=ue<=127:
            output.append({**base, 'reason':'Missing or out-of-range cover estimate'}); continue
        output.append({'date':day, 'observed_at':row['observed_at'], 'status':'available',
                       **fractions,'unmixing_error':ue})
    return output


class VegetationClient(JsonClient):
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, cache_only=False, today=None):
        super().__init__(cache_dir,session=session,cache_only=cache_only)
        self.today = today or datetime.now(ZoneInfo(TIMEZONE)).date()

    def saved_records(self, prefix, lat, lon, dates):
        """Reuse validated dated records even when a new scene changes a batch key."""
        saved = {}
        now = datetime.now(timezone.utc)
        for path in self.cache_dir.glob(f'{prefix}_*_v1_{lat:.5f}_{lon:.5f}.json'):
            try:
                envelope = json.loads(path.read_text())
                if envelope['schema'] != 1:
                    continue
                fetched = datetime.fromisoformat(envelope['fetched_at'])
                stale = not 0 <= (now-fetched).total_seconds() < 30*86400
                records = self._parse(lambda p:parse_series(p,lat,lon,dates,cached_subset=True),envelope['payload'])
                for row in records['records']:
                    if row['date'] not in saved or fetched > saved[row['date']][1]:
                        saved[row['date']] = (row,fetched,stale)
            except (OSError,ValueError,KeyError,TypeError,OverflowError):
                continue
        return saved

    def fetch(self, lat, lon, *, refresh=False):
        if type(lat) not in (int,float) or type(lon) not in (int,float) or not in_nsw(lat,lon):
            raise ValueError('Choose a NSW land point')
        lat,lon = coordinates(lat,lon,5)
        deadline = time.monotonic()+55
        common = {'service':'WMS','version':'1.3.0','request':'GetFeatureInfo',
            'crs':'EPSG:4326','bbox':f'{lat-.00015},{lon-.00015},{lat+.00015},{lon+.00015}',
            'width':3,'height':3,'i':1,'j':1,'format':'image/png','info_format':'application/json'}
        def fetch_part(namespace, layer, parse, empty, dates=None, age=30*86400):
            params = {**common,'layers':layer,'query_layers':layer}
            if dates: params['time'] = ','.join(dates)
            return self.fetch_json(namespace=namespace,source=SOURCE,lat=lat,lon=lon,
                cache_precision=5,url='https://ows.dea.ga.gov.au/',params=params,
                parse=parse,fallback=lambda:empty,max_age=age,refresh=refresh,deadline=deadline,
                fallback_note='vegetation observations unavailable; no estimates substituted')
        def catalog(payload):
            props = feature_properties(payload,lat,lon)
            dates = props.get('data_available_for_dates', [])
            # Validate the catalogue before caching, retain dates to re-filter when the day changes.
            sample_dates(dates,self.today)
            return {'dates':dates}
        available = fetch_part('dea_fc_dates','ga_ls_fc_3',catalog,{'dates':[]},age=7*86400)
        dates = sample_dates(available.data['dates'],self.today)
        parts = [available]
        samples = []
        if dates:
            prefixes = ('dea_fc_samples','dea_fc_quality')
            saved = [self.saved_records(prefix,lat,lon,dates) for prefix in prefixes]
            records = [{day:entry[0] for day,entry in cache.items()} for cache in saved]
            for cache in saved:
                if cache:
                    parts.append(DataResult({},'cached',SOURCE,min(e[1] for e in cache.values()).isoformat(),
                                            any(e[2] for e in cache.values())))
            needed = [d for d in dates if refresh or any(d not in cache or cache[d][2] for cache in saved)]
            # Latest scenes first, at most three dates per request. A timeout in an
            # older group cannot erase already obtained cover and matching quality.
            for end in range(len(needed),0,-3):
                group = needed[max(0,end-3):end]
                key = hashlib.sha256(','.join(group).encode()).hexdigest()[:12]
                parse = lambda p:parse_series(p,lat,lon,group)
                for index,layer in enumerate(('ga_ls_fc_3','ga_ls_wo_3')):
                    part = fetch_part(f'{prefixes[index]}_{key}',layer,parse,{'records':[]},group)
                    parts.append(part)
                    if part.status != 'offline':
                        for day in group:
                            records[index].pop(day,None)
                        records[index].update({r['date']:r for r in part.data['records']})
            samples = combine_samples({'records':list(records[0].values())},
                                      {'records':list(records[1].values())},dates)
        status = 'offline' if any(p.status=='offline' for p in parts) else 'live' if any(p.status=='live' for p in parts) else 'cached'
        fetched = [p.fetched_at for p in parts if p.fetched_at]
        data = {'samples':samples,'sampled_dates':dates,'resolution_m':30,
                'as_of':self.today.isoformat(),'source_url':SOURCE_URL,'method_url':METHOD_URL,
                'point':{'lat':lat,'lon':lon},
                'reason':'' if any(r['status']=='available' for r in samples) else 'No usable clear, dry sample in the selected dates.'}
        return DataResult(data,status,SOURCE,min(fetched) if fetched else None,
                          any(p.stale for p in parts),' '.join(dict.fromkeys(p.warning for p in parts if p.warning)))
