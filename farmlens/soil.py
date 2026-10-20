"""ISRIC SoilGrids point query and thickness-weighted 0–30 cm properties."""
from math import isfinite
import threading
import time

from farmlens.api import JsonClient, coordinates
from farmlens.config import SOURCE_TTLS, regional_defaults

DEPTHS = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}
PROPERTIES = {"phh2o": "ph", "clay": "clay_pct", "sand": "sand_pct", "soc": "soc_g_kg"}
_lock = threading.Lock()
_last_request = float("-inf")


def _rate_limit():
    """ISRIC permits five calls/minute; space attempts including retries."""
    global _last_request
    with _lock:
        delay = 12.1 - (time.monotonic() - _last_request)
        if delay > 0:
            time.sleep(delay)
        _last_request = time.monotonic()


def texture(clay: float, sand: float) -> str:
    return "clay-rich" if clay >= 35 else "sandy" if sand >= 65 else "medium textured"


def aggregate_soil(payload: dict) -> dict:
    try:
        layers = {layer["name"]: layer for layer in payload["properties"]["layers"]}
        data = {}
        for name, output in PROPERTIES.items():
            depths = {d["label"]: d for d in layers[name]["depths"]}
            total = 0.0
            for depth, thickness in DEPTHS.items():
                value = float(depths[depth]["values"]["mean"]) / 10
                limit = 14 if name == "phh2o" else 100 if name in ("clay", "sand") else 1000
                if not isfinite(value) or not 0 <= value <= limit:
                    raise ValueError("Invalid soil value")
                total += value * thickness / 30
            data[output] = total
        if data["clay_pct"] + data["sand_pct"] > 100:
            raise ValueError("Soil fractions exceed 100%")
        data["texture"] = texture(data["clay_pct"], data["sand_pct"])
        return data
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Missing soil property or depth") from exc


class SoilClient(JsonClient):
    def fetch(self, lat: float, lon: float, *, refresh=False):
        lat, lon = coordinates(lat, lon)
        region, defaults = regional_defaults(lat, lon)
        ph, clay, sand, soc = defaults["soil"]
        return self.fetch_json(
            namespace="soil", source="ISRIC SoilGrids", lat=lat, lon=lon,
            url="https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={"lat": lat, "lon": lon, "property": list(PROPERTIES),
                    "depth": list(DEPTHS), "value": "mean"},
            parse=aggregate_soil,
            fallback=lambda: {"ph": ph, "clay_pct": clay, "sand_pct": sand,
                              "soc_g_kg": soc, "texture": texture(clay, sand), "region": region},
            max_age=SOURCE_TTLS["soil"], refresh=refresh, before_request=_rate_limit,
        )
