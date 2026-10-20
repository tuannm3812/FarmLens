"""Fetch the three demo points and print a readable step-1 checkpoint."""
import argparse
from pathlib import Path
import sys

# Permit `python scripts/warm_cache.py` even without an editable installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from farmlens.climate import ClimateClient, frost_risk
from farmlens.config import CACHE_DIR, PRESETS
from farmlens.australian_soil import AustralianSoilClient
from farmlens.fire import FireClient
from farmlens.land_cover import LandCoverClient
from farmlens.imagery import ImageryClient
from farmlens.vegetation import VegetationClient
from farmlens.water_climate import WaterClimateClient


def label(result):
    status = "offline data" if result.status == "offline" else result.status
    return status + (", stale" if result.stale else "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Refresh even a fresh cache")
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument("--skip-fire", action="store_true", help="Skip the optional multi-year FIRMS fetch, which can take several minutes per point")
    parser.add_argument("--water-only", action="store_true", help="Warm only the optional daily rain/ET0 water-planning cache")
    parser.add_argument("--land-cover-only", action="store_true", help="Warm only the optional DEA point context")
    parser.add_argument("--vegetation-only", action="store_true", help="Warm only DEA cover and matching cloud/water masks")
    parser.add_argument("--imagery-only", action="store_true", help="Warm only NSW imagery survey metadata")
    args = parser.parse_args()
    climate = ClimateClient(args.cache_dir)
    soil = AustralianSoilClient(args.cache_dir)
    for name, (lat, lon) in PRESETS.items():
        print(f"\n{name} ({lat:.4f}, {lon:.4f})", flush=True)
        if args.imagery_only:
            imagery = ImageryClient(args.cache_dir).fetch(lat, lon, refresh=args.refresh)
            print(f"  Imagery metadata [{label(imagery)}]: {imagery.data['blocks']}", flush=True)
            continue
        if args.vegetation_only:
            cover = VegetationClient(args.cache_dir).fetch(lat,lon,refresh=args.refresh)
            usable = [r for r in cover.data['samples'] if r['status']=='available']
            print(f"  Vegetation [{label(cover)}]: {len(usable)}/{len(cover.data['samples'])} clear/dry samples",flush=True)
            if usable:
                print(f"  Latest: {usable[-1]}",flush=True)
            if cover.warning:
                print(f"  Note: {cover.warning}",flush=True)
            continue
        if not args.water_only:
            cover = LandCoverClient(args.cache_dir).fetch(lat,lon,refresh=args.refresh)
            print(f"  Land cover [{label(cover)}; {cover.data['year']}; 30 m pixel]: "
                  f"{cover.data['label'] or cover.data['reason']}",flush=True)
        if args.land_cover_only:
            continue
        water = WaterClimateClient(args.cache_dir).history(lat,lon,refresh=args.refresh)
        print(f"  Water climate [{label(water)}]: {len(water.data['dates'])} daily rain/ET0 records",flush=True)
        if water.warning:
            print(f"  Note: {water.warning}",flush=True)
        if args.water_only:
            continue
        history = climate.history(lat, lon, refresh=args.refresh)
        c = history.data
        print(f"  Climate [{label(history)}; {c['period']}]: "
              f"{c['annual_rainfall_mm']:.0f} mm/year; {c['annual_temperature_c']:.1f}°C mean; "
              f"coldest-month minimum {c['coldest_month_min_c']:.1f}°C "
              f"({frost_risk(c['coldest_month_min_c'])} frost proxy); "
              f"driest 3 months {c['driest_three_months_mm']:.0f} mm", flush=True)
        forecast = climate.forecast(lat, lon, refresh=args.refresh)
        f = forecast.data
        dates = f" ({f['start_date']} to {f['end_date']})" if f["start_date"] else ""
        print(f"  Outlook [{label(forecast)}]{dates}: {f['note']}", flush=True)
        ground = soil.fetch(lat, lon, refresh=args.refresh)
        s = ground.data
        show = lambda value: "unavailable" if value is None else f"{value:.2f}"
        print(f"  Australian SLGA [{label(ground)}]: pH {show(s['ph'])}; {s['texture']}; "
              f"clay {show(s['clay_pct'])}%; sand {show(s['sand_pct'])}%; "
              f"organic carbon {show(s['soc_g_kg'])} g/kg", flush=True)
        if not args.skip_fire:
            print("  Fire: checking three full years (can take several minutes on first fetch)…", flush=True)
            fire = FireClient(args.cache_dir).fetch(lat, lon, refresh=args.refresh)
            print(f"  Fire [{label(fire)}]: {fire.data['note']}", flush=True)
        for result in (history, forecast, ground):
            if result.warning:
                print(f"  Note: {result.warning}", flush=True)


if __name__ == "__main__":
    main()
