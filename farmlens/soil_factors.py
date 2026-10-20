"""Explicit demo soil proxies; not calibrated crop response curves."""
from math import isfinite


def valid(value, maximum):
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = float(value)
        return value if isfinite(value) and 0 <= value <= maximum else None
    except (ValueError, TypeError):
        return None


def soil_group(clay, sand):
    clay, sand = valid(clay, 100), valid(sand, 100)
    if clay is None or sand is None or clay + sand > 100:
        return None
    return "heavy" if clay >= 35 else "light" if sand >= 65 else "medium"


def texture_score(crop, clay, sand):
    group = soil_group(clay, sand)
    if group is None:
        return None
    optimal, tolerated = crop["texture_optimal"], crop["texture_tolerated"]
    if group in optimal or "wide" in optimal:
        return 100.0
    if group in tolerated or "wide" in tolerated:
        return 70.0
    return 40.0  # Unlisted is not an absolute biological limit.


def carbon_score(soc_g_kg):
    carbon = valid(soc_g_kg, 1000)
    if carbon is None:
        return None
    percent = carbon / 10
    points = ((0,50),(.8,70),(1.5,90),(2,100))
    for (lo,a),(hi,b) in zip(points,points[1:]):
        if percent <= hi:
            return a + (b-a)*(percent-lo)/(hi-lo)
    return 100.0
