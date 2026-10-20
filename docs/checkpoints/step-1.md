# Step 1 checkpoint — 20 October 2026

Climate values below were fetched from Open-Meteo ERA5 for 2016–2025 and cached locally. Forecasts were fetched for **20–26 October 2026**. SoilGrids timed out after one retry at each location; all soil values below are **offline regional demo estimates**, not measured or downloaded soil data.

| Location | Annual rainfall | Mean annual temperature | Coldest-month mean minimum | Frost proxy | Driest three months |
| --- | ---: | ---: | ---: | --- | ---: |
| Coffs Harbour | 1,414.6 mm | 20.0°C | 10.4°C | Low | 167.1 mm |
| Dubbo | 608.0 mm | 17.9°C | 4.4°C | Medium | 120.3 mm |
| Broken Hill | 174.2 mm | 18.2°C | 4.9°C | Medium | 26.0 mm |

| Location | Soil pH (offline) | Clay (offline) | Sand (offline) | SOC (offline) | Broad texture (offline) | Seven-day forecast |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Coffs Harbour | 5.50 | 25% | 45% | 25 g/kg | Medium textured | 106.0 mm rain; 13.3–28.1°C |
| Dubbo | 6.50 | 30% | 40% | 12 g/kg | Medium textured | 11.5 mm rain; 10.0–27.8°C |
| Broken Hill | 7.50 | 20% | 55% | 6 g/kg | Medium textured | 12.5 mm rain; 7.2–32.6°C |

Fire integration is deferred to step 5. No crop ranking is implemented yet; this is the requested stop before step 2.

Verification: `.venv/bin/python -m pytest -q` → **30 passed**. Streamlit scaffold loaded using `streamlit.testing.v1.AppTest` without app exceptions. `scripts/warm_cache.py` completed despite external failures; corrected ERA5 history was then fetched and cached through the same `ClimateClient` for all three presets. Six real JSON caches exist: three history and three forecast responses.

The initial live check caught ERA5-Land returning all-null rainfall. ERA5 supplied complete rainfall data. Independent review also caught scalar daily values being broadcast by pandas and dates frozen when constructing a client; regression tests cover both fixes.

Indicative only. Check with a local agronomist.
