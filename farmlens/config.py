"""Small, explicit configuration for the demo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "cache"
TIMEOUT = (5, 20)
TIMEZONE = "Australia/Sydney"
SOURCE_TTLS = {"climate":30 * 86400, "soil":180 * 86400, "forecast":4 * 3600}
# Uncalibrated demo weights; absent factors are omitted and weights renormalized.
SCORE_WEIGHTS = {"temperature": 0.20, "rainfall": 0.24, "ph": 0.16, "frost": 0.12, "fire": 0.08,
                 "texture": 0.15, "carbon": 0.05}
STRONG_MATCH_THRESHOLD = 60
FROST_THRESHOLDS = {"high": (-8, 0), "medium": (-2, 4), "low": (0, 8)}
FIRE_ABSOLUTE_LIMITS = {"high": 2, "medium": 3, "low": 4}
PRESETS = {
    "Coffs Harbour": (-30.2963, 153.1135),
    "Dubbo": (-32.2569, 148.6011),
    "Broken Hill": (-31.9539, 141.4539),
}

# Coarse illustrative regional assumptions, NOT downloaded observations.
REGIONAL_DEFAULTS = {
    "Coffs Harbour": {"climate": (1700, 19.5, 8, 220), "soil": (5.5, 25, 45, 25)},
    "Dubbo": {"climate": (580, 18, 3, 100), "soil": (6.5, 30, 40, 12)},
    "Broken Hill": {"climate": (250, 19, 4, 40), "soil": (7.5, 20, 55, 6)},
}


def regional_defaults(lat: float, lon: float) -> tuple[str, dict]:
    """Nearest of three demo regions; intentionally not a spatial soil model."""
    from math import cos, radians
    name = min(PRESETS, key=lambda n: (lat - PRESETS[n][0]) ** 2
               + ((lon - PRESETS[n][1]) * cos(radians(lat))) ** 2)
    return name, REGIONAL_DEFAULTS[name]
