"""Print and optionally save 18 cache-only crop-screening scenarios."""
import argparse
from datetime import date, datetime
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from farmlens.climate import ClimateClient
from farmlens.config import CACHE_DIR, PRESETS, TIMEZONE
from farmlens.scoring import load_crops, recommend
from farmlens.australian_soil import AustralianSoilClient


def build_scenarios(cache_dir: Path, today: date) -> list[dict]:
    climate_client = ClimateClient(cache_dir, today=today, cache_only=True)
    soil_client = AustralianSoilClient(cache_dir, cache_only=True)
    crops = load_crops()
    scenarios = []
    for location, (lat, lon) in PRESETS.items():
        climate, soil = climate_client.history(lat, lon), soil_client.fetch(lat, lon)
        for irrigation in ("rainfed", "irrigated"):
            for mode, month in (("explore", None), ("season", 5), ("season", 10)):
                result = recommend(crops, climate, soil, mode=mode, planting_month=month, irrigation=irrigation)
                scenarios.append({"location": location, "latitude": lat, "longitude": lon, "result": result})
    return scenarios


def render_markdown(scenarios: list[dict], today: date) -> str:
    lines = [f"# Step 2 checkpoint — {today.isoformat()}", "",
             "These are **provisional environmental screening candidates**, not validated planting recommendations. "
             "Scores are an uncalibrated index, not yield or probability. This report uses cache-only mode; "
             "no API calls or LLM calls were made to generate it.", "",
             "**Evidence:** real climate is used where a valid local cache exists; soil uses Australian SLGA models. Missing soil pH withholds recommendations. "
             "Every scenario below shows its own evidence status. Fire is unassessed and its weight excluded. "
             "A score of 100 means all assessed proxy factors were in their optimal ranges, not that all farm constraints were checked.", "",
             "May and October are month scenarios using historical climate, not forecasts for a specified year. "
             "Annual rainfall is still the rainfall score input in both modes. Irrigation is unquantified and gives no score bonus.", ""]
    for irrigation in ("rainfed", "irrigated"):
        lines.extend([f"## {irrigation.capitalize()} scenarios", "",
                      "| Location | Mode / month | Highest-scoring candidates | Result | Evidence |",
                      "| --- | --- | --- | --- | --- |"])
        for scenario in scenarios:
            r = scenario["result"]
            if r["irrigation"] != irrigation:
                continue
            mode = "Explore my land" if r["mode"] == "explore" else f"Plan next season / {r['planting_month']:02d}"
            candidates = "; ".join(f"{c['name']} {c['total']:.1f}" for c in r["top_three"]) or "No eligible candidates"
            status = ("Insufficient evidence or no eligible crops" if not r["ranked"] else
                      "Proxy score passes demo threshold" if r["has_strong_match"] else "No strong match")
            lines.append(f"| {scenario['location']} | {mode} | {candidates} | {status} | {r['evidence_quality']} |")
        lines.append("")
    lines.extend(["## Rainfed detail", ""])
    for scenario in scenarios:
        r = scenario["result"]
        if r["irrigation"] != "rainfed":
            continue
        mode = "Explore" if r["mode"] == "explore" else f"Season month {r['planting_month']}"
        lines.extend([f"### {scenario['location']} — {mode}", ""])
        for candidate in r["top_three"]:
            sub = candidate["subscores"]
            scores = ", ".join(f"{name} {'unassessed' if value is None else f'{value:.1f}'}" for name, value in sub.items())
            weak = ("none among assessed proxies (all tied at 100)" if all(v == 100 for v in sub.values() if v is not None)
                    else candidate["weakest_factor"])
            lines.append(f"- **{candidate['name']} — {candidate['total']:.1f}/100** ({candidate['category']}). "
                         f"Weakest factor: {weak}. Sub-scores: {scores}."
                         + (" Zero-factor cap applied." if candidate["zero_capped"] else ""))
            context = candidate["season_context"]
            if context:
                lines.append(f"  Historical growing-period context: {context['temperature_c']:.1f}°C mean; "
                             f"{context['rainfall_mm']:.1f} mm rain; {context['frost_days']:.1f} days/year below 0°C; "
                             f"{context['hot_days']:.1f} days/year at or above 35°C. Monthly mean minima "
                             "are a proxy and can conceal individual frosts.")
        if not r["top_three"]:
            lines.append("No eligible candidates with sufficient monthly data.")
        lines.append("")
    lines.extend(["## Interpretation", "",
                  "The coastal seasonal shortlist needs special scrutiny: broad global crop ranges alone can rank "
                  "lentil highly despite unassessed drainage, disease and regional production constraints. "
                  "This is an unresolved agronomic-validation gap, not evidence that lentil should be planted near Coffs Harbour. "
                  "Do not tune weights merely to obtain a more familiar-looking demonstration.", "",
                  "No strong match means all eligible candidates failed the demo's score threshold or hit an absolute limit. "
                  "Where several crops tie at the 20-point cap, their alphabetical order has no agronomic meaning. "
                  "The JSON companion contains every sub-score, excluded crop, source status and scenario warning.", "",
                  "Indicative only. Check with a local agronomist."])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(ZoneInfo(TIMEZONE)).date())
    parser.add_argument("--output-dir", type=Path, help="Save step-2.md and step-2-scenarios.json here")
    args = parser.parse_args(argv)
    scenarios = build_scenarios(args.cache_dir, args.as_of)
    markdown = render_markdown(scenarios, args.as_of)
    print(markdown)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "step-2.md").write_text(markdown, encoding="utf-8")
        (args.output_dir / "step-2-scenarios.json").write_text(
            json.dumps(scenarios, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
