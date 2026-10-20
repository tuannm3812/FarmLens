"""Validated JSON cache, bounded requests and per-source provenance."""
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import tempfile
import time
from typing import Callable, Literal

import requests

from farmlens.config import CACHE_DIR, TIMEOUT


@dataclass(frozen=True)
class DataResult:
    data: dict
    status: Literal["live", "cached", "offline"]
    source: str
    fetched_at: str | None = None
    stale: bool = False
    warning: str = ""


def coordinates(lat: float, lon: float, precision: int = 2) -> tuple[float, float]:
    lat, lon = float(lat), float(lon)
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")
    return round(lat, precision), round(lon, precision)


class JsonClient:
    def __init__(self, cache_dir: Path = CACHE_DIR, *, session=None, cache_only=False, user_agent=None):
        self.cache_dir = Path(cache_dir)
        self.session = session if session is not None else requests.Session()
        self.cache_only = cache_only
        self.user_agent = user_agent or "FarmLens/0.1 (NSW agricultural demo)"

    def fetch_json(self, *, namespace: str, source: str, lat: float, lon: float,
                   url: str, params: dict, parse: Callable[[dict], dict],
                   fallback: Callable[[], dict], max_age: int,
                   refresh: bool = False, current: Callable[[dict], bool] = lambda _: True,
                   before_request: Callable[[], None] = lambda: None,
                   decode_response: Callable = lambda response: response.json(),
                   deadline: float | None = None, cache_precision: int = 2,
                   fallback_note: str = "regional demo estimates only") -> DataResult:
        lat, lon = coordinates(lat, lon, cache_precision)
        path = self.cache_dir / f"{namespace}_v1_{lat:.{cache_precision}f}_{lon:.{cache_precision}f}.json"
        now = datetime.now(timezone.utc)
        cached = None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if envelope["schema"] != 1:
                raise ValueError("Unknown cache schema")
            data = self._parse(parse, envelope["payload"])
            fetched = datetime.fromisoformat(envelope["fetched_at"])
            age = (now - fetched).total_seconds()
            stale = not (0 <= age < max_age and current(data))
            cached = DataResult(data, "cached", source, fetched.isoformat(), stale)
            if not stale and not refresh:
                return cached
        except (OSError, ValueError, KeyError, TypeError, OverflowError):
            pass

        if self.cache_only:
            if cached:
                return DataResult(cached.data, "cached", source, cached.fetched_at, cached.stale,
                                  "Cache-only mode; cached data is stale." if cached.stale else "")
            return DataResult(fallback(), "offline", source,
                              warning=f"Offline data: no valid cache; {fallback_note} (cache-only mode).")

        failure = "Data unavailable"
        for _ in range(2):  # Original attempt plus exactly one retry.
            try:
                before_request()
                timeout = TIMEOUT
                if deadline is not None:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        failure = "TimeBudgetExceeded"
                        break
                    timeout = tuple(min(value, remaining / 2) for value in TIMEOUT)
                response = self.session.get(url, params=params, timeout=timeout,
                                            headers={"User-Agent": self.user_agent})
                response.raise_for_status()
                payload = decode_response(response)
                data = self._parse(parse, payload)
                if not current(data):
                    raise ValueError("Response does not cover the requested dates")
            except (requests.RequestException, ValueError, TypeError) as exc:
                # Do not include request URLs here: later clients may use API keys.
                failure = type(exc).__name__
                continue

            fetched_at = datetime.now(timezone.utc).isoformat()
            warning = ""
            temp_path = None
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                envelope = {"schema": 1, "source": source, "latitude": lat, "longitude": lon,
                            "fetched_at": fetched_at, "payload": payload}
                with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, suffix=".tmp",
                                                 encoding="utf-8", delete=False) as handle:
                    temp_path = Path(handle.name)
                    json.dump(envelope, handle, allow_nan=False)
                temp_path.replace(path)
            except (OSError, ValueError, TypeError):
                warning = "Live data loaded, but the cache could not be saved."
            finally:
                if temp_path is not None:
                    try:
                        temp_path.unlink(missing_ok=True)
                    except OSError:
                        pass
            return DataResult(data, "live", source, fetched_at, warning=warning)

        if cached:
            return DataResult(cached.data, "cached", source, cached.fetched_at, cached.stale,
                              f"Refresh failed ({failure}); using cached data."
                              + (" Cached data is stale." if cached.stale else ""))
        return DataResult(fallback(), "offline", source,
                          warning=f"Offline data: {source} unavailable ({failure}); {fallback_note}.")

    @staticmethod
    def _parse(parse, payload):
        try:
            return parse(payload)
        except (KeyError, TypeError, AttributeError, IndexError, OverflowError) as exc:
            raise ValueError("Malformed API response") from exc
