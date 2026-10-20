# FarmLens step 2 implementation plan

> Execute inline using the already loaded planning, test-driven development and verification skills. The user approved both modes and requested execution. Stop at the step-2 checkpoint before full UI work.

**Goal:** Implement a transparent, source-attributed crop shortlist for land exploration and preliminary seasonal planning.

**Architecture:** `data/crops.csv` holds 15 approximate crop profiles with citations. `farmlens/scoring.py` owns validated range scoring, evidence metadata and mode eligibility. Extend existing climate aggregation with monthly summaries; use existing raw caches without extra historical downloads. `scripts/demo_rankings.py` prints reproducible scenarios.

**Spec:** Original user request plus `docs/research/2026-10-20-product-and-data-review.md` and user's approval of both modes.

## Constraints and decisions
- Keep original five sub-scores and zero cap. Default weights: temperature .25, rainfall .30, pH .20, frost .15, fire .10; unknown fire is omitted and known weights renormalized.
- Frost and fire mappings are demo heuristics, identified separately from EcoCrop numerical ranges.
- Exploration uses annual temperature/rainfall and coldest-month minimum as initially requested. Seasonal mode uses selected growing-month mean temperature and coldest monthly mean minimum, retaining annual rainfall thresholds.
- Seasonal planning only admits supported annual crops in their broad month filter. Month filters do not assert local planting permission or optimal dates.
- Rainfed rice is excluded. Irrigated scenarios keep natural-rainfall screening and flag unquantified water supply; no automatic irrigation bonus.
- Rank ties deterministically by crop ID. Total <60 or any zero sub-score is not a strong match. The 60 threshold is an uncalibrated presentation choice.
- Crop category filter supports annual, pasture, perennial or all; output always retains category.
- All offline-input results are provisional; stale/unknown inputs are disclosed. Evidence coverage and score remain separate.

## Tasks
- [x] Create sourced crop CSV and data dictionary, recording approximations and broad calendar sources.
- [x] Add failing tests: trapezoid endpoints/midpoints, zero cap, missing fire, malformed weights/inputs, source loading, scenario filters and evidence states.
- [x] Add failing monthly-climate tests for precipitation totals, day counts, frost/heat indicators, year-wrapping seasons and unavailable monthly data.
- [x] Implement `load_crops()`, `range_score()`, `score_crop()` and `recommend()` in `farmlens/scoring.py`; extend `aggregate_climate()`.
- [x] Implement CLI using real cached climate and explicitly offline soil, with no new network calls by default; save diagnostic JSON and checkpoint Markdown.
- [x] Run full pytest suite, request an independent code review, fix important findings, show output and stop.

## Review focus
- Do not promote offline soil or absent fire to confidence.
- Never compare seasonal rainfall to annual requirements or automatically credit unspecified irrigation.
- Reject NaN, inverted ranges, invalid month/mode/category and inconsistent crop records.
- Avoid secretly using annual climate when seasonal summaries are unavailable.
- Report no strong match and fewer than three candidates when warranted.

## Verification

Completed 20 October 2026. Full offline pytest suite: **76 passed**. Independent code review found unchecked weather-unit metadata and overflow from extreme configurable weights; both now have regression tests and fixes. Regenerated all 18 diagnostic scenarios from cached climate and disclosed offline soil. Paused at the requested step-2 checkpoint; full UI and later integrations are not implemented.
