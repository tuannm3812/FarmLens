"""CSIRO-hosted SLGA point samples, with provenance and no synthetic fallback.

The map service supplies native pH-water units and mass percentages. It does
not expose a dependable release identifier; retain service and layer names.
"""
from concurrent.futures import ThreadPoolExecutor
from math import isfinite

from farmlens.api import DataResult, JsonClient, coordinates
from farmlens.config import CACHE_DIR, SOURCE_TTLS
from farmlens.soil import texture

BASE = "https://soils.csiro.au/arcgis/rest/services/TERN"
SOURCE = "Australian SLGA · CSIRO / TERN"
PROPERTIES = {"PHW": "ph", "CLY": "clay_pct", "SND": "sand_pct", "SOC": "soc_g_kg"}
DEPTHS = {"000_005": 5, "005_015": 10, "015_030": 15}


def parse_property(payload, code):
    """Require all three modelled depths. Missing bounds remain unknown."""
    if code not in PROPERTIES or not isinstance(payload, dict) or "error" in payload:
        raise ValueError("Invalid soil response")
    rows = {r["layerName"]: r for r in payload.get("results", [])}
    limit, multiplier = (14, 1) if code == "PHW" else (100, 10 if code == "SOC" else 1)

    def pixel(name):
        try:
            attributes = rows[name]["attributes"]
            # ArcGIS prefixes raw raster values with the renderer name.
            values = [v for k, v in attributes.items() if k == "Pixel Value" or k.endswith(".Pixel Value")]
            if len(values) != 1 or isinstance(values[0], bool):
                raise ValueError("Missing raster pixel")
            value = float(values[0])
            if not isfinite(value) or not 0 <= value <= limit:
                raise ValueError("Invalid raster value")
            return value * multiplier
        except (KeyError, TypeError) as exc:
            raise ValueError("Missing soil layer or pixel") from exc

    depths = []
    for depth, thickness in DEPTHS.items():
        layer = f"{code}_{depth}_EV_N_P_AU_TRN_N"
        value = pixel(layer)
        lower = upper = None
        try:
            lower = pixel(layer.replace("_EV_", "_05_"))
            upper = pixel(layer.replace("_EV_", "_95_"))
            if not lower <= value <= upper:
                lower = upper = None
        except ValueError:
            lower = upper = None
        depths.append({"depth_cm": depth.replace("_", "–"), "thickness_cm": thickness,
                       "value": value, "lower": lower, "upper": upper, "layer": layer})

    def weighted(field):
        return (sum(d[field] * d["thickness_cm"] / 30 for d in depths)
                if all(d[field] is not None for d in depths) else None)

    return {"value": weighted("value"), "lower": weighted("lower"), "upper": weighted("upper"),
            "depths": depths, "unit": "pH (water)" if code == "PHW" else "g/kg" if code == "SOC" else "%"}


class AustralianSoilClient:
    def __init__(self, cache_dir=CACHE_DIR, *, session=None, cache_only=False):
        self.cache_dir, self.session, self.cache_only = cache_dir, session, cache_only

    def fetch_property(self, code, lat, lon, *, refresh=False):
        if code not in PROPERTIES:
            raise ValueError("Unknown soil property")
        lat, lon = coordinates(lat, lon, 6)
        service = f"{BASE}/{code}_ACLEP_AU_TRN_N/MapServer"
        client = JsonClient(self.cache_dir, session=self.session, cache_only=self.cache_only)
        return client.fetch_json(
            namespace=f"slga_{code.lower()}", source=SOURCE, lat=lat, lon=lon,
            url=service + "/identify",
            params={"f": "json", "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
                    "sr": 4326, "layers": "all:1,2,3,5,6,7,9,10,11", "tolerance": 0,
                    "mapExtent": f"{lon-.001},{lat-.001},{lon+.001},{lat+.001}",
                    "imageDisplay": "400,400,96", "returnGeometry": "false"},
            parse=lambda payload: parse_property(payload, code),
            fallback=lambda: {"value": None, "lower": None, "upper": None, "depths": []},
            max_age=SOURCE_TTLS["soil"], refresh=refresh, cache_precision=6,
            fallback_note="soil unavailable; no estimated replacement",
        )

    def fetch(self, lat, lon, *, refresh=False):
        lat, lon = coordinates(lat, lon, 6)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {code: pool.submit(self.fetch_property, code, lat, lon, refresh=refresh)
                       for code in PROPERTIES}
            results = {code: f.result() for code, f in futures.items()}
        data = {key: results[code].data["value"] for code, key in PROPERTIES.items()}
        clay, sand = data["clay_pct"], data["sand_pct"]
        data["texture"] = (texture(clay, sand) if clay is not None and sand is not None and clay + sand <= 100
                           else "Unavailable")
        data.update(sample_latitude=lat, sample_longitude=lon, depth_cm="0–30", resolution_m=90,
                    method="Thickness-weighted modelled values; pH is an arithmetic screening proxy",
                    properties={PROPERTIES[code]: {**r.data, "status": r.status, "stale": r.stale,
                                "fetched_at": r.fetched_at, "warning": r.warning,
                                "service": f"{BASE}/{code}_ACLEP_AU_TRN_N/MapServer"}
                                for code, r in results.items()})
        missing = [key for key in PROPERTIES.values() if data[key] is None]
        status = "offline" if missing else "live" if all(r.status == "live" for r in results.values()) else "cached"
        fetched = [r.fetched_at for r in results.values() if r.fetched_at]
        warnings = (["Soil unavailable: " + ", ".join(missing) + ". No estimated replacement."] if missing else [])
        if any(r.warning and r.status != "offline" for r in results.values()):
            warnings.append("Some soil properties used cached data or could not save their cache; see property details.")
        return DataResult(data, status, SOURCE, min(fetched) if fetched else None,
                          any(r.stale for r in results.values()), " ".join(warnings))
