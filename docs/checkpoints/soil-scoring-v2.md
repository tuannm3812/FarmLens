# Soil scoring v2 checkpoint — 20 October 2026

Cache-only rainfed land exploration, using the existing Open-Meteo and Australian SLGA responses. Fire is unassessed. These are unvalidated screening indices, not probabilities or planting advice.

| Location | Clay / sand | Carbon | Top three |
| --- | --- | --- | --- |
| Coffs Harbour | 20.2% / 69.5% | 2.64% | Macadamia 100.0; Citrus (sweet orange proxy) 99.9; Improved pasture (ryegrass proxy) 90.2 |
| Dubbo | 23.5% / 65.0% | 1.30% | Canola 99.1; Olives 96.1; Lucerne 94.9 |
| Broken Hill | 24.1% / 70.5% | 0.58% | Barley 20.0; Canola 20.0; Chickpea 20.0 |

Broken Hill has no strong match: rainfall reaches an absolute limit and caps these scores at 20. Tied order has no agronomic meaning.

Texture contributes 15%, matching broad modelled sand/clay groups to the species’ EcoCrop preferences. Organic carbon contributes 5% through a shared soil-condition curve. Numeric texture penalties, broad group boundaries, the carbon curve and weights are explicitly uncalibrated demo assumptions. They are documented in [the data dictionary](../../data/README.md). Missing factors are omitted and remaining weights renormalized.

The carbon contribution can change totals but, when equally available, does not independently establish crop-specific carbon preferences. Texture provides crop-specific differentiation. Neither the data-source change nor different rankings demonstrates improved predictive accuracy.

Verification: 164 offline tests passed; browser checks covered explanations, both screening modes, preset switching, source/depth records and desktop/mobile layouts. Mobile cards fit without horizontal overflow.

Indicative only. Check with a local agronomist.
