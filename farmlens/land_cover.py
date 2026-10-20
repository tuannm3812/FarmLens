"""Dated DEA Level 3 pixel context; never a parcel or land-condition grade."""
import math
import time

from farmlens.api import JsonClient, coordinates
from farmlens.location import in_nsw

YEAR = 2025
LAYER = "ga_ls_landcover_c3"
SOURCE_URL = "https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/"
CLASSES = {111: "Cultivated vegetation", 112: "Natural / semi-natural vegetation",
           124: "Aquatic vegetation", 215: "Artificial surfaces",
           216: "Bare surfaces", 220: "Water"}


def observation(lat, lon, code=None, reason=""):
    return {"class_code": code, "label": CLASSES.get(code), "year": YEAR,
            "resolution_m": 30, "point": {"lat": lat, "lon": lon},
            "reason": reason, "source_url": SOURCE_URL}


def parse_cover(payload, lat, lon):
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise ValueError("Expected a DEA feature collection")
    features = payload["features"]
    missing = observation(lat, lon, reason="No classified pixel available at this point.")
    if not features:
        return missing
    if len(features) != 1:
        raise ValueError("Expected exactly one queried point")
    feature = features[0]
    geometry = feature["geometry"]
    point = geometry["coordinates"]
    if geometry["type"] != "Point" or len(point) != 2 or any(
        type(actual) not in (int, float) or not math.isfinite(actual) or abs(actual - expected) > .00002
        for actual, expected in zip(point, (lon, lat))
    ):
        raise ValueError("DEA returned a different point")
    records = feature["properties"].get("data", [])
    if not records:
        return missing
    if len(records) != 1 or records[0]["time"] != f"{YEAR}-01-01":
        raise ValueError("Unexpected land-cover reference year")
    code = records[0]["bands"]["level3"]
    if type(code) is not int or code not in {*CLASSES, 255}:
        raise ValueError("Unknown DEA land-cover class")
    return missing if code == 255 else observation(lat, lon, code)


class LandCoverClient(JsonClient):
    def fetch(self, lat, lon, *, refresh=False):
        if type(lat) not in (int, float) or type(lon) not in (int, float) or not in_nsw(lat, lon):
            raise ValueError("Choose a NSW land point")
        lat, lon = coordinates(lat, lon, 5)
        return self.fetch_json(
            namespace=f"dea_landcover_{YEAR}", source="DEA Land Cover (Geoscience Australia)",
            lat=lat, lon=lon, cache_precision=5, url="https://ows.dea.ga.gov.au/",
            params={"service": "WMS", "version": "1.3.0", "request": "GetFeatureInfo",
                    "layers": LAYER, "query_layers": LAYER, "styles": "level3",
                    "crs": "EPSG:4326",  # WMS 1.3.0 uses latitude-first for this CRS.
                    "bbox": f"{lat-.00015},{lon-.00015},{lat+.00015},{lon+.00015}",
                    "width": 3, "height": 3, "i": 1, "j": 1, "format": "image/png",
                    "info_format": "application/json", "time": f"{YEAR}-01-01"},
            parse=lambda payload: parse_cover(payload, lat, lon),
            fallback=lambda: observation(lat, lon, reason="Land cover unavailable; no estimate substituted."),
            max_age=30*86400, refresh=refresh, deadline=time.monotonic()+12,
            fallback_note="land cover unavailable; no estimate substituted")
