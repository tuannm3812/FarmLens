# FarmLens: product, competition and data review

Research date: 20 October 2026. Scope: a focused desk review for the one-day NSW demo. No farmer interviews or agronomist validation have been conducted. Product positioning and scoring choices below are hypotheses, not evidence of market demand or predictive accuracy.

## Decision

Build two modes on one transparent evidence pipeline:

- **Explore my land:** an initial environmental shortlist, grouping annual crops, pasture and perennial horticulture. It describes present historical suitability, not future climate resilience or financial viability.
- **Plan next season:** a preliminary shortlist of annual crops for a selected sowing month and rainfed/irrigated scenario. Show the historical climate of the selected growing period, sowing-window limitations and information still required.

Keep the requested header. Replace the stronger promise “best crops today” in explanatory copy with “Explore crop options, understand the constraints, and check this week's conditions.” The seven-day forecast is separate context and does not predict a whole growing season.

## Competitive landscape

These observations come from public first-party descriptions, not hands-on product trials. “Opportunity” is our interpretation; absence from a public page is not proof a competitor lacks a feature.

| Product or substitute | Observed offering | What FarmLens should learn |
| --- | --- | --- |
| [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home) | Species search based on environmental requirements and intended use | Matching crop ranges is already available. Make provenance, local context and limitations easy to understand. |
| [Yield Prophet](https://www.yieldprophet.com.au/yp/WhatIsYP.aspx) | APSIM simulations using crop and paddock inputs; scenarios for sowing dates, water and nitrogen | Do not describe simple range scores as yield prediction. A shortlist can precede detailed simulation and agronomist advice. |
| [Yield Prophet Lite](https://www.yieldprophet.com.au/yplite/) | Free screening for four crops using water and nitrogen inputs and explicit formulas | Low-friction, transparent tools already exist. “Free” and “explainable” alone are weak differentiators. |
| [Agworld Planning](https://www.agworld.com/products/planning/) | Collaborative field plans, operations and production budgets | Keep the demo focused on crop-option exploration; avoid reproducing a farm management suite. |
| [NSW Climate Vulnerability Assessment](https://www.dpird.nsw.gov.au/dpi/climate/climate-vulnerability-assessment/broadacre-cropping) | Historical and future climate suitability maps with commodity reports | Useful regional context, explicitly not designed for individual-holding interpretation. Do not treat maps as paddock truth. |

Proposed position: a quick NSW crop-option conversation starter that shows both suitability and evidence limitations, and lets a grower compare a land-use question with a planting-season question. Validate whether growers value this before expanding features.

## Data decisions

| Source | Evidence and access | Decision for this checkpoint |
| --- | --- | --- |
| [Open-Meteo history](https://open-meteo.com/en/docs/historical-weather-api) | Gridded reanalysis; point API; functioning ERA5 history already cached for all presets | Retain. Derive monthly climate and frost/heat-day indicators from the same daily series. Ten years is the requested recent baseline, not a standard 30-year climate normal. |
| [Open-Meteo forecast](https://open-meteo.com/en/docs) | Current short-range forecast | Retain as separately dated context; exclude from long-term scores. |
| [EcoCrop species sheets](https://ecocrop.apps.fao.org/ecocrop/srv/en/cropFindForm) | Optimal/absolute environmental ranges at species level | Transcribe the 15 requested profiles with exact sheet URLs and retrieval date. Label approximate for NSW application; do not invent cultivar precision. |
| [NSW 2026 winter crop guide](https://www.dpird.nsw.gov.au/agriculture/broadacre-crops/guides/publications/nsw-winter-crop-variety-sowing-guide) | Regional/varietal agronomy and NVT summaries | Use as a cross-check and link to it. Broad demo month filters are our simplification, not the guide's full planting recommendations. |
| [SoilGrids service](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html) | REST service reported paused; actual preset calls timed out | Keep tested adapter and explicit offline estimates. Never present these as downloaded farm soil or as high-quality evidence. |
| [Soil and Landscape Grid of Australia](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails.html) | Australian soil products, CC BY with product-specific metadata; COG and OGC access links | Preferred next soil integration to investigate. Check pH method, units, depth, uncertainty and point extraction before substituting. Documentation reviewed; no SLGA soil values fetched or integrated in this checkpoint. |
| [SILO](https://www.longpaddock.qld.gov.au/silo/about/) | Australian daily climate based on BoM observations with infilling; free CC BY 4.0 | Preferred independent climate comparison. [Point API](https://d2f1m12gua1mfo.cloudfront.net/silo/api-documentation/guide/) needs an identifying email; not configured or fetched here. |
| [FAO/IIASA GAEZ v4](https://www.fao.org/gaez/gaezv4/en) | Regional suitability for rainfed/irrigated management at 5 arc-minute resolution | A possible external benchmark, not point-level labels. v4 is a documented reference version, not a claim that it is the newest release. |

Higher resolution is not automatically greater accuracy. CSIRO documents remaining [soil-mapping limitations](https://www.csiro.au/en/research/natural-environment/land/soil/soil-inverse-modelling). Local soil tests should eventually override gridded estimates with their method, depth and sample date preserved.

## Recommendation changes

1. Keep the requested linear range scores, configurable weights and zero-score cap. Scores are an index, never a probability of crop success or expected yield.
2. Use monthly climate in seasonal mode. Annual rainfall remains an annual environmental screen; do not compare a five-month rain total with an annual EcoCrop range. Show seasonal rain separately until crop-water requirements are independently sourced.
3. Crop-specific season lengths and broad planting-month filters are explicit demo assumptions. Exact sowing dates still require region, cultivar, soil temperature and moisture. Orchard establishment is outside seasonal mode.
4. A binary irrigation choice does not quantify usable water. Retain the natural-rainfall score and label an irrigated result conditional on a water budget. Rice is excluded from the demo's rainfed shortlist; this is a NSW demo scope rule, not a global claim that rice cannot be rainfed.
5. Frost uses a disclosed, approximate cold-month-minimum proxy. Display historical frost days too. Neither assesses sensitive flowering dates, cultivar tolerance or paddock microclimate. Fire sensitivity and drought classes are separately labelled working assumptions where not supplied by the source. Drought class is descriptive, not an extra hidden score.
6. Missing fire data is **unassessed**, not “low” or a perfect score. Exclude its weight and disclose reduced coverage. Offline soil means provisional results even when scores are high.
7. Keep the three highest-scoring candidates available for inspection, but distinguish candidates from qualified recommendations. If all are poor or ineligible, say “No strong match”; never pad the list with unsuitable or out-of-season crops.

## Validation before claiming accuracy

Create 18 scenarios: the three presets × rainfed/irrigated × land exploration/May planting/October planting. Use these as reproducible software diagnostics, not expert-labelled ground truth. Record source status, eligible crops, limiting factors and rank changes. Add an independent set of NSW sites outside these presets for later agronomist review; don't tune weights to make the three demonstration towns look right.

Ask two growers and one agronomist to review the decision flow and flag unacceptable recommendations. Key interview prompts: what decision was made last season, which evidence mattered, what information would make a shortlist useful, and which outputs would cause them to distrust it? No messages have been sent to anyone.

For an expert-labelled evaluation, measure top-three acceptable-candidate coverage, contraindication errors, abstention when evidence is insufficient, and rank stability under plausible soil/rainfall changes. Hold out locations and years when calibrating. Yield trials are valuable but must not be relabelled as universal crop-choice ground truth; [NVT interpretation guidance](https://www.dpird.nsw.gov.au/agriculture/broadacre-crops/guides/publications/nsw-winter-crop-variety-sowing-guide) cautions that regional averages mask environmental interactions.

## Delivery boundary

Step 2 implements the two-mode scoring backend, source-backed crop CSV, diagnostic scenarios and printed preset results. Map controls, cards, explanations and optional integrations remain at their original steps. Stop after presenting step 2.
