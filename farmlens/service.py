"""Load only the selected point; independent sources can fail separately."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path

from farmlens.climate import ClimateClient
from farmlens.australian_soil import AustralianSoilClient
from farmlens.config import CACHE_DIR, SOURCE_TTLS


def needs_revalidation(data, now):
    """Recheck freshly-labelled session values when their source cache TTL expires."""
    for name, result in data.items():
        if name in SOURCE_TTLS and not result.stale and result.fetched_at:
            try:
                age = (now - datetime.fromisoformat(result.fetched_at)).total_seconds()
                if not 0 <= age < SOURCE_TTLS[name]:
                    return True
            except (ValueError, TypeError):
                return True
    return False


def load_point(lat, lon, *, cache_dir=CACHE_DIR, cache_only=False, refresh=False, today: date | None = None):
    climate = ClimateClient(Path(cache_dir), cache_only=cache_only, today=today)
    forecast = ClimateClient(Path(cache_dir), cache_only=cache_only, today=today)
    soil = AustralianSoilClient(Path(cache_dir), cache_only=cache_only)
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {"climate": pool.submit(climate.history, lat, lon, refresh=refresh),
                   "forecast": pool.submit(forecast.forecast, lat, lon, refresh=refresh),
                   "soil": pool.submit(soil.fetch, lat, lon, refresh=refresh)}
        return {name: task.result() for name, task in pending.items()}
