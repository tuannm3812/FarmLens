# Land overview implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Put a compact land snapshot and seven-day weather view before crop options, with seasonal graphics and progressive disclosure.

**Architecture:** Preserve the existing crop/water engines. Add an independent DEA land-cover point endpoint and a small pure frontend presentation module. Reuse cached monthly climate and expose the existing daily forecast values, with optional WMO icons.

**Tech Stack:** Existing Python 3.11, requests, pytest, vanilla JS/CSS/SVG and Leaflet; no new dependencies.

**Spec:** User approved applying the discussed Land overview: map beside land/soil and weather cards, crops below with one reason/risk, seasonal chart, collapsed water planning and evidence, short transitions. Land cover is dated context, never a health grade or score input.

## Global constraints
- Keep scores, eligibility, explanation privacy, crop photos, map naming, water calculations and Streamlit behavior intact.
- No fabricated current land status, parcel boundaries, land-cover percentages, weather or soil observations.
- DEA Collection 3 Level 3, verified 2025 annual release, native 30 m pixel at the selected point. WMS 1.3.0 EPSG:4326 uses latitude/longitude bbox order. Verify response geometry and year. Query/cache at five decimals (~1 m), not two, to avoid substituting a different 30 m pixel.
- Independent cached request with timeout/one retry; no land-cover fallback estimates. A network/source failure leaves context unavailable and never blocks crops. Cached-only mode remains respected.
- Forecast dates and stale status visible; no current flags on stale/unavailable weather. Optional missing WMO codes do not invent sunshine. Monthly climate charts require 12 valid actual monthly aggregates; regional defaults get no fabricated curve.
- Retain material local conflicts, missing evidence and provisional labels; move repeated explanations into accessible disclosures. Local fonts/palette/icons retained. Reduced-motion support and mobile stacking.

## Review focus
- WMS axis order, response pixel/year mismatch, nodata 255 and unknown classification codes.
- Delayed land-cover responses attaching to a different selected point or bypassing cached-only mode.
- Old forecast caches lacking weather codes/daily UI fields; partial/unavailable/stale weather.
- Charts obscuring missing data, implying a forecast, or clipping on mobile; keyboard-accessible alternatives.
- Crop/water/source controls remaining reachable after layout reordering and shortened text.

### Task 1: Verified observation contracts
**Files:** `farmlens/land_cover.py`, `farmlens/climate.py`, `farmlens/web.py`, `scripts/warm_cache.py`, `tests/test_land_cover.py`, `tests/test_climate.py`, `tests/test_web.py`, fixtures.
**Interfaces:** `LandCoverClient.fetch(lat,lon,refresh=False) -> DataResult` with `class_code`, `label`, `year`, `resolution_m`, `point`, `reason`; `/api/land-cover` returns its envelope without calling scoring. `aggregate_forecast` adds `days` with date/rainfall_mm/min_temperature_c/max_temperature_c/weather_code; existing aggregate keys unchanged.
- [x] Add fixture tests for genuine DEA shape, class/nodata/year/coordinate errors, retry/cache-only; endpoint isolation. Add forecast daily ordering and optional weather-code tests; observe RED.
- [x] Implement strict point client and independent endpoint; extend forecast output and cache warmer. Run Python suite GREEN.

### Task 2: Overview visuals and compact layout
**Files:** `web/overview.js`, `web/overview.css`, `web/index.html`, `web/app.js`, `web/water.js`, `tests/web_overview.test.cjs`.
**Interfaces:** `FarmLensOverview.land(soil,cover)`, `.weather(source)`, `.climate(source)` return escaped accessible markup; `.createCoverLoader(api,onUpdate)` guards request generations and reuses current context without refetching scenario-only edits.
- [x] Test fresh/stale/missing forecast, no guessed icons, 12-month charts and table, missing cover/soil, safe text, obsolete context; observe RED.
- [x] Create land and weather cards; concise crop cards; monthly aligned rainfall/temperature figures with table. Place scenario settings beside crop section; evidence and water remain on demand. Keep source-year/footprint context visible; add reduced motion transitions.
- [x] Run Node suite and syntax checks; inspect desktop/mobile presets, pin labels, crop drawer, water and sources, cache-only/unknown states.

### Task 3: Live verification and delivery
**Files:** `README.md`, `docs/research/2026-10-20-land-cover.md`, `docs/screenshots/land-overview.png`.
- [x] Fetch land cover for three public presets; record class/year/provenance and service quirks. Refresh forecast if needed to show verified daily icons.
- [x] Run complete Python/Node suites, independent final review, address important findings, save screenshot and document limits.

## Ledger
- Ruling: user already authorised applying this design; implement inline in the existing prototype. No new permission gate.
- Ruling: repository has no HEAD and all work is untracked. Continue in the current user-authorised checkout; no unsolicited initial commit/worktree or commit-based ledger scripts.
- Ruling: use a dated point classification/card for this pass; no viewport-wide WMS overlay or land-condition grading. This keeps data requests scoped to the selected point and avoids implying a farm boundary.
- Pre-flight: Task 1 adds forecast `days` and standalone land-cover envelope consumed by Task 2; scoring contracts unchanged. Raw cached forecast JSON is reparsed, so existing caches gain day values without a network refresh.
- Research: public WMS capabilities confirm `ga_ls_landcover_c3`, styles `level3`/`level4`, latest time `2025-01-01`. A WMS 1.3.0 latitude-first query at Dubbo returned class 111 and matching point; do not use the legacy 2020 layer.

- Task 1: complete — observed missing-module RED, then 255 Python tests pass. Live preset point classifications verified and recorded in research note.
- Task 2: implemented — observed frontend missing-module RED, then 19 Node tests and syntax check pass. Browser shows land/weather, seasonal charts, unchanged Canola profile and wheat water result (255 mm demand / 60 mm additional net / 0.75 ML/ha). Responsive QA in progress.

- Task 2: complete — normal desktop, 390 px mobile and 1600 px wide breakpoint checked in the in-app browser. No horizontal overflow. Verified all presets, uncached point in cache-only mode, scenario changes, crop photo/profile, water calculation, evidence tab and monthly value table. Console has no errors/warnings. Viewport override reset.
- Task 3: complete — final `.venv/bin/pytest -q` → 255 passed; `node --test tests/web_*.test.cjs` → 19 passed; both changed JavaScript files pass syntax checks. Screenshots saved under docs/screenshots/land-overview*.png. Real daily forecast WMO codes refreshed for all three presets.
- Final review: fresh gpt-6-astra reviewer found no Critical, Important or Minor defects; independently passed 64 scoped Python tests and five overview Node tests, including an extra date/code alignment check. No fix pass needed.
- Final: Ruling: reviewer deferred browser/mobile judgement — parent verified normal, mobile and wide layouts directly; accepted with screenshot evidence. Residual cost: untested device/browser combinations may vary.
- Final: Ruling: reviewer deferred live DEA accuracy — official product/capability records and real queries for all three presets verified; retain explicit 2025/30 m labels. Residual cost: classification error remains possible and requires local checking.
- Final: Ruling: explicit Refresh data overrides cache-only as in the existing app — keep the documented user-triggered refresh semantics. Residual cost: pressing Refresh deliberately makes source requests.
- Final: Ruling: existing scoring/water/Streamlit agronomic validity is outside this presentation change — leave engines intact and retain provisional/local-check language. Residual cost: existing screening assumptions still require agronomic validation.
- Delivery: updates kept in the current local prototype and existing uncommitted checkout, as requested. No branch merge, publish or repository initialization performed; Git integration menu is inapplicable because there is no HEAD or feature branch to integrate.
