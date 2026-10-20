# Land overview: source verification and limits

Verified 20 October 2026 against [Geoscience Australia's DEA Land Cover product](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/) and the [DEA OWS capabilities](https://ows.dea.ga.gov.au/?service=WMS&request=GetCapabilities).

## What is displayed

DEA Land Cover version 2.0, Collection 3, Level 3 annual classification for **2025**, native **30 m** pixel at the selected point. The verified release year is deliberately fixed rather than inferred from today's calendar. Data is CC BY 4.0, attributed to Geoscience Australia. The product is national scale; more detailed authoritative local or state mapping can differ.

The public WMS layer is `ga_ls_landcover_c3`, style `level3`, time `2025-01-01`. The legacy `ga_ls_landcover` stops at 2020 and is not used. GetFeatureInfo uses WMS 1.3.0, EPSG:4326, a latitude-first bounding box centred on the point, a 3×3 request and centre pixel (1,1). This is a point lookup, not a viewport or parcel download.

The parser requires the requested feature coordinates, reference date and known numeric class. Codes: 111 cultivated terrestrial vegetation; 112 natural/semi-natural terrestrial vegetation; 124 aquatic vegetation; 215 artificial surfaces; 216 natural bare surfaces; 220 water; 255 no data. No-data stays unavailable. Queries and cache keys use five coordinate decimals, to avoid reusing a distant pixel from the other clients' two-decimal caches. Rounding is ~1 m; the classification still represents 30 m support, not a precise parcel observation.

| Preset | Exact selected coordinates | Live 2025 class |
|---|---|---|
| Coffs Harbour | -30.2963, 153.1135 | 215 · Artificial surfaces |
| Dubbo | -32.2569, 148.6011 | 111 · Cultivated vegetation |
| Broken Hill | -31.9539, 141.4539 | 215 · Artificial surfaces |

Town presets are not asserted to be farms. Artificial-surface or water pixels display a prompt to check a nearby agricultural point. Land cover does **not** alter suitability scores, establish permission to cultivate, confirm current crop health, or claim the composition of a farm area. No percentage-area display or map overlay is inferred from Level 4 labels. A future land-use eligibility feature would require separate agronomic and regulatory design.

## Reliability and display

The standalone `/api/land-cover` request has a timeout, one retry, a 12-second request budget and a 30-day validated JSON cache. Network inactivity timeouts do not impose a strict total limit on continuously streaming responses. Failure uses cache or an explicit unavailable state; no regional land-cover estimates are fabricated. It cannot block `/api/analyze`. Request generations prevent late results from appearing under a new point, and scenario-only changes reuse the cover request.

The seven-day strip uses the actual Open-Meteo daily dates, rainfall and minimum/maximum temperatures already behind the aggregate outlook. Optional WMO weather codes drive the icons; old caches without codes show a thermometer, not guessed sunshine. Stale outlooks retain their dates and have no current temperature flags. Seasonal charts use all twelve validated historical monthly means, aligned in separate rainfall and temperature panels with a numeric table. Regional fallback climate has no invented seasonal curve.

The land card labels SLGA soil as modelled, 0–30 cm. Cover is annual satellite context, weather is forecast, and climate is historical reanalysis; none is a live soil-moisture or land-health measurement.
