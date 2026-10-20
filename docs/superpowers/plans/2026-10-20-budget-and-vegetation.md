# Crop budget and vegetation cover implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Add the approved wheat/barley/canola financial scenarios and a real DEA vegetation-cover chart to the local FarmLens app.
**Architecture:** Separate optional panels; neither modifies suitability scores. Python validates and calculates budgets and reads/caches DEA point observations. Small vanilla JS modules render accessible results and guard asynchronous location changes.
**Tech Stack:** Existing Python 3.11, requests, local HTTP server, vanilla JS/CSS/SVG, pytest and node:test.
**Spec:** Approved conversation descriptions: editable gross margin, break-even yield/price, low/base/high scenarios; green/dry/bare vegetation chart with dated observations. Implementation choices below fill in the details.

## Global constraints
- Work in the user's existing local demo. No commits or worktree fork: this repository has no HEAD and all existing work is untracked.
- Preserve current crop-scoring and water-planning behavior.
- AUD per cropped hectare, excluding GST. Gross margin excludes fixed overheads and is not net profit.
- No inferred yield, current-price claims, or synthetic satellite observations. Financial blanks remain unknown.
- Archived examples load only by explicit button; source, 2012 date and Central West dryland scope remain visible after edits.
- Only selected-point satellite calls; timeout, one retry per request, cache, unavailable fallback. Fine-grained satellite cache keys.
- Concise visible summaries; formulas, sources and limitations in disclosures.

## Review focus
- Zero yield/price, blank or negative/nonfinite inputs: no invented break-even values.
- Archived values must not be mistaken for a current, location-specific farm forecast.
- Cloudy/nodata/invalid or mismatched DEA observations must not turn into measured cover.
- Late responses or new pins must not display the previous point's chart or budget inputs.
- Keyboard and narrow screens must retain labels and numeric alternatives to charts.

## Task 1: Financial calculation and source records
Files: farmlens/budget.py, data/budget_profiles.json, tests/test_budget.py.
Interfaces: budget_metadata() -> dated profiles; assess_budget(payload) -> rows with revenue, total variable costs, gross margin, break-even price/yield and sensitivity cases.
- [x] Test literal arithmetic including per-tonne selling costs and per-hectare irrigation; reject negatives, booleans, nonfinite values; blank inputs return unavailable, real zero remains zero.
- [x] Run failing tests, then implement cost = variable_per_ha + irrigation_per_ha + selling_per_t * yield. Gross margin = yield * price - cost. Break-even yield = per_ha costs / (price - selling_per_t); price = selling_per_t + per_ha costs / yield. Undefined denominators return null.
- [x] Test +/-20% yield and price cases with costs per hectare held fixed and per-tonne costs following yield. Label sensitivity assumptions, not probabilities.
- [x] Store only verified NSW archived summary figures and links; explicitly describe the simplified fixed-cost treatment.

## Task 2: DEA point observations
Files: farmlens/vegetation.py, tests/test_vegetation.py, tests/fixtures/vegetation_*.json.
Interfaces: VegetationClient.fetch(lat, lon, refresh=False) -> DataResult with observations, sampled dates, completeness, pixel resolution and source URL.
- [x] Verify WMS dates and quality fields using one public demo point before implementation.
- [x] Test real fixture parsing, matching geometry/date, finite 0–100 cover fractions, nodata/missing quality exclusion, cache/retry and no-cache abstention.
- [x] Fetch a bounded set of observed dates and preserve actual observation times. Show separate 0–100 bars (never silently normalise fractions to sum to 100).
- [x] Treat trend as sampled observations, with gaps explicit; no interpolation of missing observations or claims of daily availability.

## Task 3: Routes and optional panels
Files: farmlens/web.py, web/budget.js, web/vegetation.js, web/insights.css, web/index.html, web/app.js, tests/test_web.py, tests/web_budget.test.cjs, tests/web_vegetation.test.cjs.
Interfaces: /api/budget and /api/vegetation; bootstrap includes budget metadata. Both modules expose mount(api/metadata) and setContext(point) following water.js.
- [x] Test route isolation, invalid point/input rejection, escaped labels, missing values, stale data and asynchronous invalidation.
- [x] Add compact vegetation panel near snapshot/weather, budget panel next to water feasibility. Load optional satellite history on demand, reuse cached same-point data, reset location-specific financial inputs when point/water mode changes.
- [x] Financial form starts empty; explicit archived-example button enables a demonstrable comparison with provenance. Three crops stay in stable order, not a profit ranking.
- [x] Add reference links to current ABARES market indicators; no automatic use of indicator prices as local farm-gate prices.

## Task 4: Verify and document
Files: README.md, scripts/warm_cache.py, docs/screenshots/.
- [x] Add vegetation-only warm-cache option; verify real preset responses and unavailable states.
- [x] Run full pytest and Node suites; restart local server and check desktop/mobile, inputs, location changes, loading, dates and sources.
- [x] Fresh-context review of the financial and vegetation boundaries; fix material issues with regression tests.
- [x] Record actual source coverage and limitations; deliver screenshot and local app link.

## Execution record
- Source research: NSW Central West winter budgets are March 2012 archived examples. Use wheat short-fallow after cereal, feed barley, conventional canola; no current-year default estimates.
- DEA probe: a date interval returned only its first observation; time-series requests need explicit dates and no rendering style. Verify before integrating.
- Plan and implementation continue inline under the user's instruction to add both approved features.

- Completed 20 October 2026. Fresh-context review identified stale budget inputs during pending/failed point changes and cache loss across changing satellite catalogues. Both fixed with failing-then-passing regression tests. Bounded three-date batches retain usable prior records.
- Full verification after the final code edit: 287 Python tests and 28 JavaScript tests passed; JS syntax checks passed. Browser checks covered desktop and 390-pixel viewport, real charts, archived budgets, zero yield, cleared inputs on point changes and no horizontal overflow. No browser console errors.
- Live/cache checkpoint: Coffs Harbour 5/12 usable (latest 2026-08-31), Dubbo 5/12 (2026-10-07; partial service timeouts), Broken Hill 7/12 (2026-09-24). Missing or excluded observations remain gaps.
- Saved budget-comparison.png, vegetation-cover.png and vegetation-mobile.png in docs/screenshots/. README describes the archived financial examples, satellite method, caching and limits. Local server remains running on port 8503.
