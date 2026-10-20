"""Complete historical FIRMS coverage before classifying a 25 km exposure proxy."""
import csv
from datetime import date, datetime, timedelta
from io import StringIO
from math import asin, cos, degrees, radians, sin, sqrt
import os
import time
from urllib.parse import quote
from zoneinfo import ZoneInfo

from farmlens.api import DataResult, JsonClient, coordinates
from farmlens.config import CACHE_DIR, TIMEZONE

SENSOR = "VIIRS_SNPP_SP"
RADIUS_KM = 25
# Uncalibrated demonstration thresholds for a fixed three-year, single-sensor window.
MEDIUM_COUNT = 10
HIGH_COUNT = 100


def csv_payload(response):
    reader=csv.DictReader(StringIO(response.text))
    if not reader.fieldnames:
        raise ValueError("Missing CSV headers")
    return {"fields":reader.fieldnames,"rows":list(reader)}


def date_windows(start, end):
    cursor=start
    while cursor<=end:
        last=min(cursor+timedelta(days=4),end)
        yield cursor,last
        cursor=last+timedelta(days=1)


def _availability(payload):
    if not {"data_id","min_date","max_date"}.issubset(payload["fields"]):
        raise ValueError("Missing availability columns")
    rows=[row for row in payload["rows"] if row["data_id"]==SENSOR]
    if len(rows)!=1:
        raise ValueError("Missing sensor availability")
    start,end=date.fromisoformat(rows[0]["min_date"]),date.fromisoformat(rows[0]["max_date"])
    if start>end:
        raise ValueError("Invalid availability interval")
    return {"start":start.isoformat(),"end":end.isoformat()}


def _distance(lat,lon,other_lat,other_lon):
    dlat,dlon=radians(other_lat-lat),radians(other_lon-lon)
    a=sin(dlat/2)**2+cos(radians(lat))*cos(radians(other_lat))*sin(dlon/2)**2
    return 2*6371.0088*asin(sqrt(min(1,max(0,a))))


def count_detections(payload, lat, lon, start, end):
    required={"latitude","longitude","acq_date","acq_time","satellite"}
    if not required.issubset(payload["fields"]):
        raise ValueError("Missing fire detection columns")
    unique=set()
    for row in payload["rows"]:
        rlat,rlon=float(row["latitude"]),float(row["longitude"])
        coordinates(rlat,rlon)
        acquired=date.fromisoformat(row["acq_date"])
        clock=int(row["acq_time"])
        if not start<=acquired<=end or not 0<=clock//100<24 or not 0<=clock%100<60 or not row["satellite"]:
            raise ValueError("Invalid detection date/time or satellite")
        if _distance(lat,lon,rlat,rlon)<=RADIUS_KM:
            unique.add((rlat,rlon,acquired,clock,row["satellite"]))
    return {"count":len(unique)}


class FireClient(JsonClient):
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, cache_only=False, map_key=None, today=None):
        super().__init__(cache_dir,session=session,cache_only=cache_only)
        self.map_key=os.getenv("FIRMS_MAP_KEY","") if map_key is None else map_key
        self.today=today or datetime.now(ZoneInfo(TIMEZONE)).date()

    def fetch(self, lat, lon, *, refresh=False, max_seconds=None, progress=None):
        lat,lon=coordinates(lat,lon)
        start,end=date(self.today.year-3,1,1),date(self.today.year-1,12,31)
        base={"count":None,"exposure":None,"complete":False,"radius_km":RADIUS_KM,
              "period":f"{start.year}–{end.year}","sensor":SENSOR}
        def missing(note):
            return DataResult({**base,"note":note},"offline","NASA FIRMS",warning=note)
        if not self.map_key.strip():
            return missing("fire data not configured")
        key=quote(self.map_key.strip(),safe="")
        clock=time.monotonic()
        deadline=None if max_seconds is None else clock+max_seconds
        availability=self.fetch_json(namespace=f"firms_availability_{SENSOR}",source="NASA FIRMS availability",
            lat=lat,lon=lon,url=f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{key}/{SENSOR}",
            params={},parse=_availability,fallback=lambda:{},max_age=86400,refresh=refresh,decode_response=csv_payload,deadline=deadline)
        if availability.status=="offline":
            return missing("Fire history unavailable; complete historical coverage could not be verified.")
        if not date.fromisoformat(availability.data["start"])<=start<=end<=date.fromisoformat(availability.data["end"]):
            return missing(f"Fire history unavailable: the source does not cover all of {base['period']}.")
        delta=degrees(RADIUS_KM/6371.0088)
        longitude_delta=degrees(asin(sin(radians(delta))/cos(radians(lat))))
        box=f"{lon-longitude_delta:.6f},{lat-delta:.6f},{lon+longitude_delta:.6f},{lat+delta:.6f}"
        windows=list(date_windows(start,end))
        results=[availability]
        count=0
        for index,(a,b) in enumerate(windows):
            if max_seconds is not None and time.monotonic()-clock>=max_seconds:
                return missing(f"Fire history incomplete ({index}/{len(windows)} intervals checked). Fetch again to resume from cached intervals.")
            chunk=self.fetch_json(namespace=f"firms_{SENSOR}_r25_{a}_{b}",source="NASA FIRMS detections",lat=lat,lon=lon,
                url=f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{SENSOR}/{box}/{(b-a).days+1}/{a}",params={},
                parse=lambda p,a=a,b=b:count_detections(p,lat,lon,a,b),fallback=lambda:{},
                max_age=365*86400,refresh=refresh,decode_response=csv_payload,deadline=deadline)
            if chunk.status=="offline":
                return missing(f"Fire history incomplete ({index}/{len(windows)} intervals checked); exposure remains unassessed.")
            count+=chunk.data["count"]
            results.append(chunk)
            if progress:
                progress((index+1)/len(windows))
        exposure="high" if count>=HIGH_COUNT else "medium" if count>=MEDIUM_COUNT else "low"
        warning=" ".join(dict.fromkeys(r.warning for r in results if r.warning))
        return DataResult({**base,"count":count,"exposure":exposure,"complete":True,
                           "note":f"{count} active-fire detections within 25 km during {base['period']}; {exposure} exposure proxy."},
                          "live" if any(r.status=="live" for r in results) else "cached","NASA FIRMS",
                          min(r.fetched_at for r in results if r.fetched_at),any(r.stale for r in results),warning)
