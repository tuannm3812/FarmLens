# Seasonal water feasibility implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.

**Goal:** A separate historical water scenario for wheat, barley and canola, estimating crop demand and additional irrigation without changing crop rankings.

**Architecture:** A separately cached Open-Meteo ERA5 daily rain/FAO-56 ET0 client feeds a deterministic daily storage balance. An on-demand `/api/water` endpoint serves a progressive-disclosure panel in the existing custom app. No new dependencies or OpenAI calls.

**Tech Stack:** Python 3.11, requests, pandas, vanilla JS/CSS, pytest, Node tests.

**Spec:** The user selected the Water feasibility option: seasonal demand and irrigation shortfall for wheat, barley and canola alongside the score. The implementation choices below bound this pilot and are not agronomic validation.

## Global constraints and design
- Preserve all current crop scores, weights, ranking, NSW eligibility, explanation payloads and Streamlit behavior.
- Use a separate request only when Calculate is pressed for the selected NSW point. Cache JSON by rounded coordinates and year range; bounded timeout, one retry, validated cache fallback. No regional ET0 defaults: missing data means unavailable.
- Fetch 11 complete calendar years, then select the latest 10 complete crop seasons ending by the last full calendar year. This handles seasons crossing New Year without mixing an incomplete current season into the sample.
- Use daily `rain_sum` (liquid rainfall, not snowfall) and `et0_fao_evapotranspiration`, mm, ERA5, Australia/Sydney. Require every date, finite nonnegative values, correct units and timezone.
- FAO-56 Table 12 coefficients: spring-type wheat 0.30/1.15/0.25; barley 0.30/1.15/0.25; canola 0.35/1.10/0.35. Canola 1.10 is a disclosed choice within the cited 1.0–1.15 range. Fixed coefficients are not adjusted for local wind, humidity or wetting frequency.
- Illustrative four-stage durations: cereals 20/30/60/40 days (150 total; general small-grain example in FAO Table 11); canola 30/40/70/40 (180 total; explicit demo assumption). All four stage lengths are editable. Wheat is a spring-type proxy, not a winter/dormancy model.
- Sowing on day 1 of a selected month is a scenario, not a sowing recommendation. Flag months outside existing broad crop calendars. All three are available for water comparison even when absent from the shortlist; water does not establish eligibility.
- Daily ETc = ET0 × Kc, constant initially/mid-season and linear through development/late stages. Rain infiltration is a user scenario percentage. Retain infiltrated rain only to the entered soil buffer; excess is excluded. Draw ETc from storage; unmet demand is additional net water. No future rain offsets an earlier deficit.
- Soil buffer is readily available storage before stress, not total plant-available water capacity. Its default 100 mm and starting 50 mm are explicitly illustrative, never inferred from SLGA. Initial storage must not exceed the buffer. Root growth, stress response, capillary rise, salinity and delivery constraints are not modelled.
- Default rain infiltration 80% and irrigation efficiency 80% are editable assumptions, not measurements. Gross demand ML/ha = net mm / efficiency / 100. Rainfed supply is zero; irrigated supply is optional and unknown when blank. Never turn unknown supply into zero or confirmed feasibility.
- Show per-metric median and historical 10th–90th percentile range (linear interpolation, not forecast/confidence limits), exact 10 season date ranges, input/source provenance, remaining shortfall if supply entered, and a historical table. No success-probability badge or automatic irrigation schedule.
- Keep user assumptions local to `/api/water`; clear results on changes, abort obsolete requests, reset land-specific assumptions on location change. Mobile layout, keyboard controls and textual chart alternatives required.

## Review focus
- Delayed rain must not erase an earlier shortfall; rainfall above storage capacity cannot be banked indefinitely.
- Missing/invalid daily data and stale caches must remain explicit and never yield invented feasible results.
- Cross-year and leap-day seasons must have exact coverage; current partial years are excluded.
- Unknown supply, zero supply, invalid percentages, booleans/NaN and initial storage above capacity must be distinguished and validated before network access.
- A late water response must not attach to another point or altered assumptions; water analysis must not change crop rankings.

### Task 1: Reliable daily water climate client
**Files:** `farmlens/water_climate.py`, `tests/test_water_climate.py`, `tests/fixtures/water_history.json`.
**Interface:** `WaterClimateClient.history(lat, lon, refresh=False) -> DataResult`; data has `dates`, `rain_mm`, `et0_mm`, `start_year`, `end_year`, `grid` metadata. Offline data uses empty lists.
- [x] Write fixture-backed tests for complete dates/units, invalid/null/boolean values, retry/cache fallback, rounded point and year range; observe RED.
- [x] Implement separate namespaced cache, source metadata and strict validation; run client tests GREEN.

### Task 2: Deterministic scenario and isolated API
**Files:** `farmlens/water.py`, `data/water_profiles.json`, `tests/test_water.py`, `tests/test_web.py`, `farmlens/web.py`, `scripts/warm_cache.py`.
**Interfaces:** `water_metadata() -> dict`; `validate_water_inputs(payload) -> dict`; `kc_curve(profile, stages) -> list[float]`; `daily_balance(rain, et0, kc, inputs) -> dict`; `assess_water(DataResult, inputs) -> dict`. `POST /api/water` returns `{source, assessment}` without daily arrays; bootstrap includes water metadata.
- [x] Write tests for hand-calculated balance, storage overflow/rain timing, gross/net conversion, unknown/zero supply, validation, stage curves, exact ten complete seasons, stale/offline evidence, and endpoint isolation; observe RED.
- [x] Implement calculator and API; preserve score/explain routes. Add optional `--water-only` prewarming and water warming to standard presets. Run Python suite GREEN.

### Task 3: Water panel, documentation and verification
**Files:** `web/water.js`, `web/index.html`, `web/app.js`, `web/style.css`, `tests/web_water.test.cjs`, `README.md`, `docs/research/2026-10-20-water-method.md`.
- [x] Test presentation of unknown versus zero water supply, unavailable/stale history and escaped metadata; observe RED then implement.
- [x] Add crop/month/supply controls, editable assumptions and explicit Calculate button. Include source/method disclosure, median/range results and per-season table. Abort/reset stale results when context or inputs change.
- [x] Verify real preset API access, record checkpoint results and sources; if service fails verify honest unavailable UI and cache recovery.
- [x] Run full pytest, Node suite and JS syntax checks; desktop/mobile browser checks including invalid input, changed point/assumptions, rainfed/irrigated and photo/ranking regression.
- [x] Fresh independent final review; fix material issues, save screenshot and update README.

## Progress and decisions
- User has authorized this milestone. Implement in the existing local prototype without another permission gate.
- Repository still has no HEAD; current working tree is the authorized prototype. No initial commit/worktree is created; this document retains the ledger instead of commit-based scripts.
- Data-source choice: Open-Meteo keeps the pilot credential-free and consistent with existing climate; SILO remains an independent comparison candidate. Cost: this is not an independent Australian climate cross-check.
- Pre-flight interfaces: Task 1 data feeds Task 2 only; Task 2 metadata and assessment feed Task 3. No changes to the scoring data contract.

- Task 1 complete: 15 client tests passed after missing-module RED. Fixture is synthetic and explicitly test-only; live preset verification is in progress.

- Task 2 complete: all 230 Python tests pass. Live rain/ET0 history returned 4,018 dates for each preset. Ten-season outputs calculated independently of scoring.
- Task 3 complete: four new Node cases passed RED→GREEN (11 total). Final verification: 230 Python tests passed in 3.10 seconds; all 11 Node cases passed; both frontend JavaScript syntax checks passed.
- Independent review confirmed the daily balance, complete seasons, input validation, request invalidation and score separation. Fixed both findings: invalid inputs inside collapsed assumptions now reopen the section and show the error; the fixed historical endpoint fixture test now freezes its clock. Review suggested mounted-form automation as a future coverage improvement; real browser checks exercised these event paths for this pilot.
- Browser verification: default wheat and canola outputs; rainfed, blank, zero and 2 ML/ha supplies; invalid/cross-field inputs and reset; new-location reset from Dubbo to Broken Hill; planting-month synchronization; historical table and source disclosure; crop photo and score regression. At a 390-pixel mobile viewport, the page had no horizontal overflow and the wide table stayed within its own scroll region. Temporary viewport override reset; no browser warnings/errors captured.
- Live checkpoint: all three presets returned 4,018 actual ERA5 daily records. Nine crop/location scenarios recorded in `docs/checkpoints/water-feasibility.json` and `.md`; model accuracy remains unvalidated. Saved final Dubbo rainfed scenario to `docs/screenshots/water-feasibility.png` and documented the source, assumptions and limitations in README and the research note.
