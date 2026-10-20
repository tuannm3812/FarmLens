"""Rate-limited Nominatim place searches and map-pin locality labels."""
from dataclasses import replace
import hashlib
import os
import threading
import time
import requests

from farmlens.api import JsonClient, coordinates
from farmlens.config import CACHE_DIR
from farmlens.location import in_nsw

_lock = threading.Lock()
_last_request = float("-inf")


def _rate_limit(*,deadline=None):
    global _last_request
    if deadline is None:
        _lock.acquire()
    else:
        remaining=deadline-time.monotonic()
        if remaining<=0 or not _lock.acquire(timeout=remaining):
            raise requests.Timeout('Geocoder rate-limit deadline exceeded')
    try:
        delay = 1.05 - (time.monotonic() - _last_request)
        if deadline is not None and time.monotonic()+max(0,delay)>=deadline:
            raise requests.Timeout('Geocoder rate-limit deadline exceeded')
        if delay > 0:
            time.sleep(delay)
        _last_request = time.monotonic()
    finally:
        _lock.release()


def _parse(payload):
    if not isinstance(payload, list):
        raise ValueError("Expected search results")
    matches=[]
    for item in payload:
        lat,lon=float(item["lat"]),float(item["lon"])
        coordinates(lat,lon)  # validate, retaining original pin precision
        name=item["display_name"]
        if not isinstance(name,str) or not name.strip():
            raise ValueError("Missing location label")
        if item.get("address",{}).get("country_code") == "au" and in_nsw(lat,lon):
            matches.append({"name":name,"lat":lat,"lon":lon})
    return {"matches":matches}


def _parse_reverse(payload):
    if not isinstance(payload,dict):
        raise ValueError('Expected reverse-geocoding result')
    unknown={'name':None,'kind':None}
    if payload.get('error')=='Unable to geocode':
        return unknown
    address=payload['address']
    if not isinstance(address,dict):
        raise ValueError('Expected address components')
    if address.get('country_code')!='au' or not (
        address.get('state')=='New South Wales' or address.get('ISO3166-2-lvl4')=='AU-NSW'):
        return unknown
    # Never label a point with a nearby private property, building or road name.
    for field in ('suburb','locality','village','hamlet','town','city','municipality','county','state_district'):
        value=address.get(field)
        if isinstance(value,str) and 0<len(value.strip())<=200:
            return {'name':f'{" ".join(value.split())}, NSW',
                    'kind':'area' if field in ('municipality','county','state_district') else 'locality'}
    return unknown


class Geocoder(JsonClient):
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, cache_only=False):
        super().__init__(cache_dir,session=session,cache_only=cache_only,
                         user_agent=os.getenv("NOMINATIM_USER_AGENT") or "FarmLens/0.1 (NSW crop screening demo)")
        self.url=os.getenv("NOMINATIM_URL") or "https://nominatim.openstreetmap.org/search"
        self.reverse_url=os.getenv('NOMINATIM_REVERSE_URL') or 'https://nominatim.openstreetmap.org/reverse'

    def search(self, query, *, refresh=False):
        query=" ".join(query.strip().lower().split())
        if not 2 <= len(query) <= 250:
            raise ValueError("Enter a place or address between 2 and 250 characters.")
        digest=hashlib.sha256((self.url+query).encode()).hexdigest()
        result=self.fetch_json(namespace=f"geocode_{digest}",source="Nominatim / OpenStreetMap",lat=0,lon=0,
            url=self.url,params={"q":query,"format":"jsonv2","countrycodes":"au","addressdetails":1,"limit":5},
            parse=_parse,fallback=lambda:{"matches":[]},max_age=30*86400,refresh=refresh,before_request=_rate_limit)
        if result.status == "offline":
            result=replace(result,warning="Address search unavailable and no valid cache exists. Choose a preset or click the map.")
        return result

    def reverse(self,lat,lon,*,refresh=False):
        if isinstance(lat,bool) or isinstance(lon,bool) or not in_nsw(lat,lon):
            raise ValueError('Choose a point on land inside NSW.')
        lat,lon=coordinates(lat,lon)
        digest=hashlib.sha256(self.reverse_url.encode()).hexdigest()
        deadline=time.monotonic()+12
        result=self.fetch_json(namespace=f'reverse_locality_{digest}',source='Nominatim / OpenStreetMap',lat=lat,lon=lon,
            url=self.reverse_url,params={'lat':lat,'lon':lon,'format':'jsonv2','addressdetails':1,'zoom':12,'accept-language':'en'},
            parse=_parse_reverse,fallback=lambda:{'name':None,'kind':None},max_age=30*86400,
            refresh=refresh,before_request=lambda:_rate_limit(deadline=deadline),deadline=deadline,
            fallback_note='place name unavailable; retain selected coordinates')
        if result.status=='offline':
            result=replace(result,warning='Place name unavailable. The selected coordinates are unchanged.')
        return result
