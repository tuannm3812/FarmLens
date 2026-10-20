# Australian soil integration — 20 October 2026

Live CSIRO SLGA point queries succeeded for all four properties at all three demo locations. Depth-weighted modelled values for 0–30 cm:

| Point | pH in water | Clay % | Sand % | Organic carbon g/kg |
| --- | ---: | ---: | ---: | ---: |
| Coffs Harbour | 5.03 | 20.22 | 69.50 | 26.38 |
| Dubbo | 6.55 | 23.46 | 65.00 | 13.02 |
| Broken Hill | 7.77 | 24.06 | 70.50 | 5.83 |

The previous hard-coded pH values were 5.5, 6.5 and 7.5. The app and cache-warming/ranking scripts now use Australian SLGA. Missing soil pH withholds recommendations; regional soil constants are no longer used in those paths. The old SoilGrids client is retained separately for compatibility.

Explore / rainfed rankings remain unchanged for these particular presets: Coffs Harbour has ryegrass-proxy pasture (100), macadamia (100), sweet-orange-proxy citrus (99.9); Dubbo has barley, canola, chickpea (all 100); Broken Hill has the same three tied at the 20 cap, with **no strong match**. This is expected because crop pH ranges are broad and Broken Hill is rainfall-limited. A better source does not by itself demonstrate better predictive accuracy. Clay, sand and carbon are context; only pH enters the present score.

Source: [CSIRO SLGA map services](https://soils.csiro.au/arcgis/rest/services/TERN), [official soil attribute descriptions](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html). Modelled grid (~90 m), historical input observations, not current farm tests. Per-layer bounds and precise query coordinates are exposed in the UI; the weighted uncertainty envelope is not a joint confidence interval. Retrieval date is not product release or soil sampling date.

Indicative only. Check with a local agronomist.

Verification: 130 offline tests pass; Python compilation and dependency checks pass. Browser inspection at desktop and mobile widths confirmed summary, soil provenance, seasonal scores, rule-based explanations and responsive cards. Independent code review identified the distinction between missing evidence and a failed match; the UI and ranking report now reserve “No strong match” for assessed candidates. Saved screenshots: `docs/screenshots/australian-soil-ui.jpg` and `docs/screenshots/australian-soil-shortlist.jpg`.
