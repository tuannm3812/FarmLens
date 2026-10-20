"""Transparent screening, not a yield model or a probability of success."""
import csv
import math
from pathlib import Path

from farmlens.api import DataResult
from farmlens.agronomy import assess_guidance, load_guidance, DRAINAGE_OPTIONS
from farmlens.soil_factors import texture_score, carbon_score, soil_group
from farmlens.config import ROOT, SCORE_WEIGHTS, STRONG_MATCH_THRESHOLD, FROST_THRESHOLDS, FIRE_ABSOLUTE_LIMITS

RANGE_SUFFIXES = ("abs_min", "opt_min", "opt_max", "abs_max")
CATEGORIES = {"annual", "pasture", "perennial"}


def _finite(value):
    if isinstance(value, bool):
        raise ValueError("Expected a finite number, not a boolean")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Expected a finite number")
    return value


def range_score(value, absolute_min, optimal_min, optimal_max, absolute_max) -> float:
    value, lo, best_lo, best_hi, hi = map(_finite, (value, absolute_min, optimal_min, optimal_max, absolute_max))
    if not lo < best_lo <= best_hi < hi:
        raise ValueError("Invalid absolute/optimal ranges")
    if value <= lo or value >= hi:
        return 0.0
    if best_lo <= value <= best_hi:
        return 100.0
    if value < best_lo:
        return 100 * (value - lo) / (best_lo - lo)
    return 100 * (hi - value) / (hi - best_hi)


def load_crops(path: Path = ROOT / "data" / "crops.csv") -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        crops = list(csv.DictReader(handle))
    seen = set()
    for crop in crops:
        try:
            if not crop["id"] or crop["id"] in seen or crop["category"] not in CATEGORIES:
                raise ValueError("Invalid or duplicate crop identity")
            seen.add(crop["id"])
            for prefix in ("temp", "rain", "ph"):
                for suffix in RANGE_SUFFIXES:
                    key = f"{prefix}_{suffix}"
                    crop[key] = _finite(crop[key])
                range_score(crop[f"{prefix}_opt_min"], *[crop[f"{prefix}_{s}"] for s in RANGE_SUFFIXES])
            for key in ("frost_tolerance", "drought_tolerance", "fire_sensitivity"):
                if crop[key] not in {"high", "medium", "low"}:
                    raise ValueError("Invalid tolerance class")
            for key in ("texture_optimal", "texture_tolerated"):
                crop[key] = crop[key].split(";")
                if not crop[key] or any(v not in {"light","medium","heavy","organic","wide"} for v in crop[key]):
                    raise ValueError("Invalid crop texture profile")
            crop["ecocrop_id"] = int(crop["ecocrop_id"])
            crop["growing_months"] = int(crop["growing_months"])
            crop["planting_months"] = [int(m) for m in crop["planting_months"].split(";") if m]
            if not 1 <= crop["growing_months"] <= 12 or any(not 1 <= m <= 12 for m in crop["planting_months"]):
                raise ValueError("Invalid crop calendar")
            if crop["requires_irrigation"] not in ("0", "1"):
                raise ValueError("Invalid irrigation flag")
            crop["requires_irrigation"] = crop["requires_irrigation"] == "1"
            if crop["source_url"] != f"https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id={crop['ecocrop_id']}":
                raise ValueError("Missing or inconsistent source citation")
        except (KeyError, TypeError) as exc:
            raise ValueError("Incomplete crop profile") from exc
    if not crops:
        raise ValueError("No crop profiles")
    return crops


def score_crop(crop: dict, *, temperature_c: float, rainfall_mm: float, ph: float,
               frost_min_c: float, fire_exposure: str | None = None, weights=None,
               clay_pct=None, sand_pct=None, soc_g_kg=None) -> dict:
    weights = dict(SCORE_WEIGHTS if weights is None else weights)
    if set(weights) == {"temperature","rainfall","ph","frost","fire"}:
        weights.update(texture=0.0, carbon=0.0)
    if set(weights) != set(SCORE_WEIGHTS):
        raise ValueError("Weights must name all seven factors")
    weights = {key: _finite(value) for key, value in weights.items()}
    if any(value < 0 for value in weights.values()) or max(weights.values()) <= 0:
        raise ValueError("Weights must be non-negative and have a positive sum")
    # Ratios are unchanged, while multiplication and addition cannot overflow.
    scale = max(weights.values())
    weights = {key: value / scale for key, value in weights.items()}
    if not 0 <= _finite(ph) <= 14 or _finite(rainfall_mm) < 0:
        raise ValueError("Invalid soil pH or rainfall")
    if fire_exposure not in (None, "low", "medium", "high"):
        raise ValueError("Unknown fire exposure")
    values = {"temperature": (temperature_c, "temp"), "rainfall": (rainfall_mm, "rain"), "ph": (ph, "ph")}
    subscores = {key: range_score(value, *[crop[f"{prefix}_{s}"] for s in RANGE_SUFFIXES])
                 for key, (value, prefix) in values.items()}
    floor, optimum = FROST_THRESHOLDS[crop["frost_tolerance"]]
    subscores["frost"] = max(0.0, min(100.0, 100 * (_finite(frost_min_c) - floor) / (optimum - floor)))
    subscores["fire"] = None
    if fire_exposure is not None:
        exposure = {"low": 0, "medium": 1, "high": 2}[fire_exposure]
        limit = FIRE_ABSOLUTE_LIMITS[crop["fire_sensitivity"]]
        subscores["fire"] = max(0.0, 100 * (1 - exposure / limit))
    subscores["texture"] = texture_score(crop, clay_pct, sand_pct)
    subscores["carbon"] = carbon_score(soc_g_kg)
    assessed = {key: value for key, value in subscores.items() if value is not None}
    denominator = math.fsum(weights[key] for key in assessed)
    if denominator <= 0:
        raise ValueError("No positive weight on assessed factors")
    total = (math.fsum((value / 100) * weights[key] for key, value in assessed.items()) / denominator) * 100
    capped = any(value == 0 for value in assessed.values())
    final = min(total, 20.0) if capped else total
    return {"id": crop["id"], "name": crop["name"], "category": crop["category"],
            "total": final, "uncapped_total": total, "subscores": subscores,
            "weakest_factor": min(assessed, key=assessed.get), "zero_capped": capped,
            "strong_match": final >= STRONG_MATCH_THRESHOLD and not capped,
            "assessed_weight_pct": (denominator / math.fsum(weights.values())) * 100,
            "source_url": crop["source_url"], "notes": crop["notes"]}


def season_context(climate: dict, planting_month: int, growing_months: int) -> dict:
    if type(planting_month) is not int or not 1 <= planting_month <= 12:
        raise ValueError("Planting month must be 1–12")
    if type(growing_months) is not int or not 1 <= growing_months <= 12:
        raise ValueError("Growing period must be 1–12 months")
    try:
        monthly = climate["monthly"]
        lookup = {m["month"]: m for m in monthly}
        if len(monthly) != 12 or set(lookup) != set(range(1, 13)):
            raise ValueError("Complete monthly climate required")
        months = [(planting_month - 1 + offset) % 12 + 1 for offset in range(growing_months)]
        selected = [lookup[month] for month in months]
        for row in selected:
            for field in ("temperature_c", "minimum_c", "rainfall_mm", "days", "frost_days", "hot_days"):
                _finite(row[field])
            if row["days"] <= 0 or any(row[f] < 0 for f in ("rainfall_mm", "frost_days", "hot_days")):
                raise ValueError("Invalid monthly climate")
        days = sum(row["days"] for row in selected)
        return {"months": months,
                "temperature_c": sum(row["temperature_c"] * row["days"] for row in selected) / days,
                "frost_min_c": min(row["minimum_c"] for row in selected),
                "rainfall_mm": sum(row["rainfall_mm"] for row in selected),
                "frost_days": sum(row["frost_days"] for row in selected),
                "hot_days": sum(row["hot_days"] for row in selected)}
    except (KeyError, TypeError) as exc:
        raise ValueError("Monthly climate unavailable") from exc


def recommend(crops: list[dict], climate: DataResult, soil: DataResult, *, mode="explore",
              planting_month=None, irrigation="rainfed", category=None, fire_exposure=None,
              weights=None, drainage="unknown") -> dict:
    if drainage not in DRAINAGE_OPTIONS:
        raise ValueError("Invalid drainage scenario")
    catalogue = load_guidance()
    if mode not in {"explore", "season"} or irrigation not in {"rainfed", "irrigated"}:
        raise ValueError("Invalid mode or irrigation scenario")
    if category is not None and category not in CATEGORIES:
        raise ValueError("Invalid crop category")
    if mode == "season" and (type(planting_month) is not int or not 1 <= planting_month <= 12):
        raise ValueError("Season mode requires a planting month from 1–12")
    warnings = ["Approximate crop ranges and unvalidated demo weights; scores are not success probabilities."]
    evidence = "modelled inputs — not field validated"
    sources = {"climate": climate, "soil": soil}
    try:
        soil_available = 0 <= _finite(soil.data.get("ph")) <= 14
    except (ValueError, TypeError):
        soil_available = False
    if not soil_available:
        warnings.append("Soil pH is unavailable or invalid; crop recommendations are withheld. Fetch Australian soil data or choose a cached location.")
    if any(result.stale for result in sources.values()):
        evidence = "provisional — stale inputs"
    if any(result.status == "offline" for result in sources.values()):
        evidence = "provisional — offline inputs"
    for source, result in sources.items():
        if result.status == "offline":
            warnings.append(f"{source.capitalize()}: offline or incomplete inputs; obtain local evidence before acting.")
        if result.stale:
            warnings.append(f"{source.capitalize()}: stale cached data.")
    if fire_exposure is None:
        warnings.append("Fire exposure unassessed; fire weight excluded, not treated as low risk.")
    if irrigation == "irrigated":
        warnings.append("Irrigated scenario: water budget unverified; natural rainfall score retained without an irrigation bonus.")
    if mode == "season":
        warnings.append("Preliminary month filter only; region, variety, soil moisture and soil temperature still need checking.")
    warnings.append("NSW guidance checks can withhold conflicting candidates; remaining crops still need local checks and are not agronomically validated.")
    warnings.append("Texture classes and 100/70/40 penalties are broad demo proxies; organic carbon is a shared soil-condition factor, not a crop-specific fertility test.")
    if soil_group(soil.data.get("clay_pct"), soil.data.get("sand_pct")) is None:
        warnings.append("Texture unavailable or inconsistent; its weight is excluded.")
    if carbon_score(soil.data.get("soc_g_kg")) is None:
        warnings.append("Organic carbon unavailable or invalid; its weight is excluded.")
    ranked, excluded, guidance_excluded = [], {}, []
    for crop in crops:
        reason = None
        if category is not None and crop["category"] != category:
            reason = "Different crop category"
        elif crop["requires_irrigation"] and irrigation == "rainfed":
            reason = "Requires irrigation in this NSW demo"
        elif mode == "season" and crop["category"] != "annual":
            reason = "Perennial/pasture establishment not supported in seasonal mode"
        elif mode == "season" and planting_month not in crop["planting_months"]:
            reason = "Outside the supported broad planting-month filter"
        if reason:
            excluded[crop["id"]] = reason
            continue
        context = None
        if mode == "season":
            try:
                context = season_context(climate.data, planting_month, crop["growing_months"])
            except ValueError:
                excluded[crop["id"]] = "Monthly climate unavailable or invalid"
                continue
        if not soil_available:
            excluded[crop["id"]] = "Soil pH unavailable or invalid"
            continue
        result = score_crop(crop,
                            temperature_c=context["temperature_c"] if context else climate.data["annual_temperature_c"],
                            rainfall_mm=climate.data["annual_rainfall_mm"], ph=soil.data["ph"],
                            frost_min_c=context["frost_min_c"] if context else climate.data["coldest_month_min_c"],
                            fire_exposure=fire_exposure, weights=weights,
                            clay_pct=soil.data.get("clay_pct"), sand_pct=soil.data.get("sand_pct"),
                            soc_g_kg=soil.data.get("soc_g_kg"))
        group = soil_group(soil.data.get("clay_pct"), soil.data.get("sand_pct"))
        result["soil_context"] = {"group":group, "optimal":crop["texture_optimal"],
                                  "tolerated":crop["texture_tolerated"],
                                  "carbon_note":"Shared 0–30 cm soil-condition proxy; not measured nutrient availability."}
        result["season_context"] = context
        result["inputs"] = {"temperature_c": context["temperature_c"] if context else climate.data["annual_temperature_c"],
                            "annual_rainfall_mm": climate.data["annual_rainfall_mm"], "ph": soil.data["ph"],
                            "frost_min_c": context["frost_min_c"] if context else climate.data["coldest_month_min_c"]}
        result["inputs"].update({key:soil.data.get(key) for key in ("clay_pct","sand_pct","soc_g_kg")})
        result["guidance"] = assess_guidance(crop["id"], climate, irrigation=irrigation,
                                             drainage=drainage, catalogue=catalogue)
        if result["guidance"]["status"] == "conflict":
            guidance_excluded.append(result)
            excluded[crop["id"]] = " ".join(check["message"] for check in result["guidance"]["checks"]
                                               if check["status"] == "conflict")
        else:
            ranked.append(result)
    if any("Monthly" in reason for reason in excluded.values()):
        warnings.append("Monthly climate is missing or invalid; affected seasonal crops were not scored.")
    ranked.sort(key=lambda result: (-result["total"], result["id"]))
    return {"mode": mode, "planting_month": planting_month, "irrigation": irrigation,
            "category": category, "drainage": drainage, "guidance_version": catalogue["version"],
            "guidance_excluded": guidance_excluded, "ranked": ranked, "top_three": ranked[:3], "excluded": excluded,
            "has_strong_match": any(result["strong_match"] for result in ranked),
            "evidence_quality": evidence, "warnings": warnings,
            "sources": {name: {"source": r.source, "status": r.status,
                               "fetched_at": r.fetched_at, "stale": r.stale} for name, r in sources.items()}}
