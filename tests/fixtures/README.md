# Deterministic API fixtures

These JSON files are **synthetic fixtures in documented API response shapes**, not observations from the preset locations. They keep tests independent of the network.

- `history.json`: complete 2016–2025 daily series including leap days. Each month's rainfall totals `month_number * 10` mm, so annual rainfall is 780 mm and the three driest months total 60 mm. Daily maxima are 20°C, minima 10°C except July (0°C). Seven ordinary and three leap years give mean annual temperature 14.5756905457°C.
- `forecast.json`: seven days, 20–26 October 2026, 12 mm rain, temperature range 6–28°C.
- `soil.json`: different values at all three depths to detect accidental unweighted averaging. Weighted outputs: pH 6⅓, clay 23⅓%, sand 41⅔%, organic carbon 11⅔ g/kg.

Reference shapes: [Open-Meteo](https://open-meteo.com/en/docs), [SoilGrids REST](https://rest.isric.org/soilgrids/v2.0/docs).

- `geocode.json`: synthetic Australian search results, with NSW matches and an excluded Victorian result.
- `firms.json`: CSV response strings in a JSON fixture: source date availability, two unique nearby detections, a duplicate, a detection outside 25 km and a valid empty interval.
- `explanation.json`: synthetic structured model output for one anonymous crop index. No real OpenAI call is made in tests.
