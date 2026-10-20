# Water feasibility pilot: method and limits

The pilot is a historical scenario comparison for wheat, barley and canola. It is independent of crop scores, eligibility rules and model explanations. It does not predict yield, prescribe irrigation dates, or validate the crop for a selected farm.

## Evidence

- [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api) supplies daily liquid rainfall (`rain_sum`) and FAO-56 reference evapotranspiration (`et0_fao_evapotranspiration`), both in mm. FarmLens explicitly selects ERA5 and Australia/Sydney dates. This is reanalysis, not a paddock station measurement. The returned grid coordinates and retrieval time are retained.
- [FAO-56 Chapter 6](https://www.fao.org/4/x0490e/x0490e0b.htm), Tables 11/12 and its coefficient-curve method, provide the crop-demand framework. Daily potential crop demand is reference ET multiplied by a stage-dependent coefficient. These reference coefficients assume standard conditions; the pilot does not adjust them for local wind, humidity or wetting frequency.
- [NSW soil moisture monitoring guidance](https://www.nsw.gov.au/regional-and-primary-industries/agriculture/soil/soil-moisture/moisture-monitoring) explains the importance of active-root-zone monitoring and timely irrigation before stress. It does not validate FarmLens's storage assumptions. FarmLens does not use a soil texture or carbon score to fabricate water capacity.

SILO remains a useful independent Australian climate comparison. This first integration uses the already-established, key-free Open-Meteo service. It makes no claim to be a SILO integration or an independent climate cross-check. The synthetic Kaggle irrigation model is not used.

## Crop inputs

The versioned profile catalogue is `data/water_profiles.json`.

| Profile | Initial / mid / end coefficient | Default stage days | Status |
| --- | --- | --- | --- |
| Wheat | 0.30 / 1.15 / 0.25 | 20 / 30 / 60 / 40 | Spring-type wheat coefficient proxy and general small-grain duration example; not a winter-dormancy model |
| Barley | 0.30 / 1.15 / 0.25 | 20 / 30 / 60 / 40 | Generic coefficient and duration example |
| Canola | 0.35 / 1.10 / 0.35 | 30 / 40 / 70 / 40 | Mid coefficient is selected within the published 1.0–1.15 range; stage durations are explicit FarmLens assumptions |

All four stage lengths are editable. None is a calibrated NSW cultivar calendar. Fixed day counts do not represent temperature-dependent phenology. The curve is constant in the initial and mid stages, linearly increasing through development and decreasing through the late stage. Transition days use the end-of-day fraction (1/L through L/L), avoiding duplicate boundary days.

Sowing is modelled on day 1 of the chosen month. Existing broad sowing windows are disclosed; an out-of-window calculation is flagged rather than interpreted as approval. All three water profiles remain available even when crop eligibility checks exclude them from the main shortlist. Wheat and barley deliberately return the same water values for identical inputs; the pilot cannot distinguish varieties or management responses.

## Daily balance

Defaults are scenario assumptions: 100 mm usable soil-water buffer, 50 mm available at sowing, 80% rainfall infiltration and 80% irrigation efficiency. They are not measured or inferred values for the selected point. Inputs reset on a location change.

The buffer represents readily available root-zone storage **before stress**, not total plant-available water capacity. Starting water must be between zero and the buffer. For each day:

1. Multiply rainfall by the chosen infiltration fraction.
2. Retain only what fits into the remaining buffer. Exclude excess water.
3. Compute potential crop demand as ET0 × Kc.
4. Draw demand from storage; accumulate any unmet amount as additional net water. Storage cannot become negative.

Later rainfall cannot erase an earlier deficit. The gross irrigation estimate divides the additional net water by efficiency. One ML per hectare equals 100 mm. Entered gross irrigation supply is converted with the same efficiency and compared with the accumulated deficit; a blank irrigated supply is unknown, while a rainfed scenario supplies zero irrigation.

The model effectively assumes water can arrive exactly when needed and uses a fixed buffer throughout growth. It does not simulate delivery restrictions, application events, growing roots, stress feedback, crop failure, runoff routing, waterlogging, salinity or capillary rise. It may understate practical irrigation needs. Retained rain includes any water remaining in storage at harvest and is not necessarily all consumed. No pumping/area/economic calculation is implied by ML/ha; the user divides an allocation by irrigated hectares before entering it.

## Historical sample and summaries

Fetch the last 11 complete calendar years (2015–2025 for the 2026 demo), then choose the latest ten complete crop seasons that fit. A May season uses starts 2016–2025; a November season crossing New Year uses 2015–2024. Leap days are retained. This avoids introducing incomplete 2026 observations or forecasts.

Each season is simulated separately. Medians and 10th–90th percentiles use linear interpolation on ten results. They describe that sample only; they are neither prediction intervals nor confidence intervals. Medians from different metrics need not sum. A count of historical seasons with residual shortfall is not a future probability or a suitability score.

## Reliability and validation

The water endpoint queries only the selected point when requested. It has a separate year-versioned cache, coordinate rounding to two decimals, the shared 5-second connection/20-second read timeout, one retry, a 30-day freshness window and validated stale-cache fallback. Every expected day, array length, unit, numeric value and timezone is checked. Without valid daily history it abstains; there is no regional ET0 fallback. Stale provenance remains visible. UI requests are cancelled/invalidated on context or input changes, with a 60-second frontend timeout.

Tests cover hand-calculated daily storage, rainfall timing/overflow, unit conversion, unknown supply, invalid inputs, coefficient interpolation, cross-year/leap-day completeness, retry/cache paths and isolation from crop scoring. These tests establish software behavior, not agronomic accuracy. The next external validation step is comparison with measured soil-water records and locally calibrated crop-stage/ET data, reviewed by an agronomist.
