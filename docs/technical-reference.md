# Methods and limitations

FarmLens combines sourced environmental inputs with explicit screening rules.
The result is a provisional comparison, not a yield forecast, profit prediction
or probability of crop success. See the [architecture](2_architecture.md) for
components and the [data dictionary](../data/README.md) for exact crop parameters.

## Crop screening

The [15 crop profiles](../data/crops.csv) use approximate FAO EcoCrop ranges and
disclosed proxy species. Temperature, annual rainfall and pH score 100 inside
preferred ranges, falling linearly to zero at the absolute limits.

| Factor | Configured weight | Interpretation |
| --- | ---: | --- |
| Temperature | 20% | Historical temperature against approximate crop ranges |
| Rainfall | 24% | Annual rainfall screen, not available growing-season water |
| Soil pH | 16% | Modelled pH in water; not interchangeable with CaCl₂ pH |
| Frost | 12% | Cold-month minimum-temperature proxy; not event probability |
| Fire exposure | 8% | Historical detection category and assumed crop sensitivity |
| Texture | 15% | Broad soil groups and crop preferences; penalties are assumptions |
| Organic carbon | 5% | Shared soil-condition curve, not crop-specific nutrient sufficiency |

The total is a weighted mean of assessed factors. Missing factors are omitted
and weights renormalised; they do not receive perfect scores. Any assessed zero
caps the total at 20. Missing soil pH withholds the shortlist. Scores and curves
are implemented in [scoring.py](../farmlens/scoring.py), with weights in
[config.py](../farmlens/config.py).

The app returns up to three eligible crops, their factor scores and weakest
assessed factor. Ties use crop ID; tied capped scores do not convey a meaningful
preference. A 60-point presentation threshold with no zero factor marks a strong
*proxy* match. This threshold and all weights remain uncalibrated.

### Modes and NSW guidance

- **Explore my land** compares annual environmental requirements across annual
  crops, pasture and perennial horticulture.
- **Plan next season** filters supported annual crops by planting month and uses
  historical growing-month temperature and frost summaries. Annual rainfall
  remains an annual screen; this is not a seasonal weather forecast.
- **Rainfed / irrigated** describes a scenario. Irrigation earns no score bonus
  because usable supply is not established. Rice is withheld in the rainfed
  demo as an explicit scope rule.

The [NSW guidance catalogue](../data/nsw_guidance.json) adds source-linked checks
without changing EcoCrop ranges or calibrating the weights. With compatible fresh
historical rainfall, rainfed macadamia below 1,200 mm/year and lentil at or below
300 mm/year are withheld. Reported poor drainage withholds five sensitive crops;
drainage is never inferred from texture. Unknown or incompatible checks stay
unassessed. Review [source compatibility and remaining constraints](research/2026-10-20-nsw-scoring-validation.md)
before interpreting a candidate. A passed check is not approval to plant.

## Climate and Australian soil

**Historical climate:** [Open-Meteo ERA5](https://open-meteo.com/en/docs/historical-weather-api)
supplies the last ten complete calendar years (2016–2025 for the 2026 showcase).
Annual rainfall is the mean of annual totals. Annual temperature averages daily
(maximum + minimum) / 2 within each year, then across years. The frost proxy is
the mean daily minimum in the climatological coldest month. Driest-three-month
rainfall sums the three driest monthly climatological totals; the months need
not be consecutive. Incomplete series are rejected. ERA5 is reanalysis, not a
farm weather-station record.

**Forecast:** the separate [seven-day outlook](https://open-meteo.com/en/docs)
includes today in Australia/Sydney time. Cached forecasts keep their actual
dates and stale labels. Forecasts do not change rankings; missing outlooks are
not replaced with typical climate.

**Soil:** [CSIRO / TERN SLGA](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html)
provides modelled pH in water, clay, sand and organic carbon at approximately
90 m resolution. Values at 0–5, 5–15 and 15–30 cm are thickness-weighted to 0–30 cm
using 5/30, 10/30 and 15/30. Native pH is used directly; carbon percent × 10 gives
g/kg. Arithmetic pH averaging is a screening approximation. Retained lower/upper
layers form a depth-weighted envelope, not a joint confidence interval.

Broad texture groups use ≥35% clay for clay-rich soil, ≥65% sand for sandy soil,
and otherwise medium texture. Invalid sand/clay totals suppress the label.
These groups do not establish drainage, rooting depth or water-holding capacity.
The grid is not a current farm soil test. Missing soil remains unknown; the
legacy SoilGrids client is retained in code but is not the app's active source.

## Water and budget scenarios

The **water pilot** compares wheat, barley and canola over ten complete historical
seasons using daily ERA5 liquid rain and FAO-56 reference evapotranspiration.
Potential demand is ET0 × crop coefficient. A fixed daily storage balance tracks
rain infiltration, crop demand and unmet water; later rain cannot erase an earlier
deficit. Gross irrigation is net gap divided by efficiency; 100 mm = 1 ML/ha.

Stage timing, 100 mm storage, 50 mm starting water and 80% infiltration/efficiency
are editable illustrative defaults, not measurements derived from SLGA. Blank
irrigated supply is unknown. Historical medians and 10th–90th percentiles describe
the sample, not forecast intervals. See the [full water method](research/2026-10-20-water-method.md)
and [versioned parameters](../data/water_profiles.json).

The **budget calculator** uses entered yield, price and variable costs to show
gross margin per hectare, break-even values and ±20% yield/price sensitivity.
Gross margin excludes overheads, finance and tax. FarmLens does not infer yield
from the soil or crop score. The optional 2012 NSW Central West examples are
archived illustrations, not current returns; their source PDFs and assumptions
are retained in [budget_profiles.json](../data/budget_profiles.json).

Both tools are independent of rankings. Water feasibility does not establish
crop eligibility, and a budget scenario is not a profit forecast.

## Imagery, land cover and fire

**NSW imagery** is a dated aerial/satellite mosaic with survey-block metadata
from [NSW Spatial Services](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer).
Block dates do not certify the date of every surrounding pixel. Missing imagery
or dates stay unavailable; no generated image represents selected land.

**DEA land cover** is a fixed 2025 annual class at a 30 m pixel, not a farm-wide
land-use survey. [Source and resolution details](research/2026-10-20-land-cover.md)
explain the town-centre demo points and land-use cautions.

**DEA vegetation cover** shows green vegetation, dry vegetation and bare ground
at a 30 m pixel. Up to twelve monthly scenes are sampled from the preceding year.
Only matching clear/dry Water Observations quality flags permit a result; gaps
remain visible. Independent estimates are not forced to total 100%. This is
[historical satellite context](https://knowledge.dea.ga.gov.au/data/product/dea-fractional-cover-landsat/),
not current crop health or yield. Imagery, land cover and vegetation do not alter
crop scores or establish permission to cultivate.

**NASA FIRMS**, when configured, counts VIIRS S-NPP standard-product detections
within 25 km over the last three complete calendar years. Fewer than 10, 10–99
and 100+ detections map to low, medium and high exposure. These are uncalibrated
demo thresholds, not NASA hazard categories. Detections are not unique fires or
burned area. Missing or partial coverage stays unassessed. Credentialed live
FIRMS coverage has not been verified for this showcase.

## Reliability, privacy and validation

Source clients use bounded timeouts, one retry and validated JSON caches. Failed
refreshes can use labelled stale evidence. Coordinates use source-appropriate
precision: two decimals for climate/fire, six for Australian soil, and five for
imagery metadata and DEA context. Cache records retain retrieval times. Runtime
caches are not distributed with the repository.

Only climate has labelled regional demonstration fallbacks. Missing soil,
forecast, land cover and vegetation are not replaced with invented observations.
Seasonal mode abstains without valid monthly history. Selected-point requests
send coordinates to the relevant providers; map tiles and imagery may still need
internet in cached mode.

Finn answers supported report questions locally. Typed guide questions stay in
the browser. Optional OpenAI crop wording uses the numeric allowlist in
[explain.py](../farmlens/explain.py); addresses, coordinates, crop names and guide
conversation are excluded. Wording cannot change scores. Nominatim search is
submitted explicitly, throttled and cached in the single-process local server.

Run `python scripts/check.py` for offline fixture tests, Python compilation and
JavaScript checks. [CI results](https://github.com/tuannm3812/FarmLens/actions/workflows/check.yml)
verify software behaviour, not agronomic accuracy. Remaining work is agronomist
review, measured field comparisons and calibration by region, season and cultivar.

Indicative only. Check with a local agronomist.
