"""NSW imagery survey metadata; imagery itself is displayed by the browser."""

from datetime import datetime, timezone
import math
import time

from farmlens.api import JsonClient, coordinates
from farmlens.location import in_nsw

DATES_URL = (
    "https://maps.six.nsw.gov.au/arcgis/rest/services/public/"
    "NSW_Imagery_Dates/MapServer/0/query"
)
SOURCE_URL = (
    "https://maps.six.nsw.gov.au/arcgis/rest/services/public/"
    "NSW_Imagery/MapServer"
)


def parse_metadata(payload: dict, lat: float, lon: float) -> dict:
    """Retain every intersecting survey block without inventing pixel dates."""
    features = payload.get("features")
    if "error" in payload or not isinstance(features, list) or len(features) > 50:
        raise ValueError("Invalid imagery metadata")
    blocks = []
    for feature in features:
        attrs = feature["attributes"]
        name = attrs["BlockName"]
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 200:
            raise ValueError("Invalid survey block")
        stamp = attrs.get("BlockStartDate")
        survey_date = None
        if stamp is not None:
            if type(stamp) not in (int, float) or not math.isfinite(stamp):
                raise ValueError("Invalid survey date")
            date = datetime.fromtimestamp(stamp / 1000, tz=timezone.utc)
            if date.year < 1900 or date.date() > datetime.now(timezone.utc).date():
                raise ValueError("Invalid survey date")
            survey_date = date.date().isoformat()
        resolution = attrs.get("Resolution_cm")
        if resolution is not None and (
            type(resolution) not in (int, float)
            or not math.isfinite(resolution)
            or not 0 < resolution <= 100000
        ):
            raise ValueError("Invalid imagery resolution")
        blocks.append(
            {"name": name.strip(), "survey_date": survey_date,
             "resolution_cm": resolution}
        )
    return {
        "blocks": blocks, "point": {"lat": lat, "lon": lon},
        "source_url": SOURCE_URL,
        "date_note": "Survey block metadata at the pin; surrounding pixels may differ.",
    }


class ImageryClient(JsonClient):
    def fetch(self, lat: float, lon: float, *, refresh: bool = False):
        """Query only the selected NSW point with a fine-grained cache key."""
        if type(lat) not in (int, float) or type(lon) not in (int, float) or not in_nsw(lat, lon):
            raise ValueError("Choose a NSW land point")
        lat, lon = coordinates(lat, lon, 5)
        return self.fetch_json(
            namespace="nsw_imagery_dates", source="NSW Spatial Services",
            lat=lat, lon=lon, cache_precision=5, url=DATES_URL,
            params={
                "f": "json", "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint", "inSR": 4326,
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "BlockName,BlockType,BlockStartDate,Resolution_cm",
                "returnGeometry": "false",
            },
            parse=lambda payload: parse_metadata(payload, lat, lon),
            fallback=lambda: parse_metadata({"features": []}, lat, lon),
            max_age=30 * 86400, refresh=refresh,
            deadline=time.monotonic() + 12,
            fallback_note="survey date unavailable; no date substituted",
        )
