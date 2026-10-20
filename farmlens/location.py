"""Local NSW boundary checks using the bundled ABS 2021 state geometry."""
from functools import lru_cache
import json
import math

from farmlens.config import ROOT


@lru_cache(maxsize=1)
def boundary():
    return json.loads((ROOT / "data" / "nsw_boundary.geojson").read_text())


def _inside_ring(x, y, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


@lru_cache(maxsize=1)
def _polygons():
    result = []
    for polygon in boundary()["features"][0]["geometry"]["coordinates"]:
        xs, ys = zip(*polygon[0])
        result.append(((min(xs), min(ys), max(xs), max(ys)), polygon))
    return result


def in_nsw(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if not math.isfinite(lat) or not math.isfinite(lon):
            return False
        for (west, south, east, north), polygon in _polygons():
            if west <= lon <= east and south <= lat <= north:
                if _inside_ring(lon, lat, polygon[0]) and not any(_inside_ring(lon, lat, hole) for hole in polygon[1:]):
                    return True
    except (ValueError, TypeError):
        return False
    return False
