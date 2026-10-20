# NSW guidance consistency review — 20 October 2026

**Outcome:** FarmLens has been checked against NSW guidance, not validated against crop outcomes. The seven-factor weighted score is still an uncalibrated environmental screen. A source-backed eligibility layer now withholds clear conflicts and exposes missing checks. It does not replace the score with invented NSW response curves or claim measured accuracy gains.

## What changed

The versioned [guidance catalogue](../../data/nsw_guidance.json) covers all 15 crop profiles. Each check retains a publication title, edition/date where known, page/section and source URL. Checks are `met`, `not_assessed` or `conflict`; every candidate still has unassessed agronomic constraints. A single met check is not approval to plant.

- Rainfed macadamia: the NSW 2023 new-orchard guide calls for supplementary irrigation below 1,200 mm/year. Fresh historical modelled annual rainfall below that threshold withholds it from the rainfed shortlist. At the boundary it remains conditional. This recent ten-year climate average is a screening comparison, not a forecast or guaranteed water supply.
- Rainfed lentil: the 2026 winter guide specifies annual rainfall above 300 mm. At or below 300 mm it is withheld. Irrigated scenarios leave this rainfed requirement unassessed because a water budget is missing.
- User-reported poor drainage: canola, chickpea, lentil, macadamia and lucerne are withheld until the conflict is resolved. Unknown drainage remains unknown. A report of good drainage only passes that specific user-reported check, not the crop assessment. Drainage resets on changing locations. Texture is never used to infer it. Withheld does not mean cultivation is permanently impossible after suitable remediation.
- Fallback/stale rainfall cannot trigger a new NSW rainfall exclusion. The original baseline scores still show the effect of those provisional inputs.
- Known conflicts are listed with reasons and sources, rather than silently disappearing. The underlying numeric score is preserved for audit, not reduced by a made-up penalty.

## Winter crops and macadamia

| Crop | Guidance and principal missing checks | Current disposition |
| --- | --- | --- |
| Wheat | 2026 winter guide pp. 4–5, 15, 21: regional cultivar/flowering timing | Broad month screen remains provisional |
| Barley | Same guide pp. 40–45: cultivar differences, including waterlogging tolerance | No universal drainage rejection |
| Oats | Same guide pp. 55–64: grain, hay and grazing uses differ | Grain proxy only |
| Canola | Same guide p. 74: acidity by depth, seedbed moisture, nitrogen and constraints | Drainage gate; other checks unresolved |
| Chickpea | Same guide p. 97: pHCa, aluminium, chloride, drainage and late-spring frost | Drainage gate; no PHW conversion |
| Lentil | Same guide pp. 140–141: rainfall, pHCa, drainage and subsoil constraints | Rainfall/drainage gates; depth tests unresolved |
| Macadamia | 2023 guide pp. 9, 18: water, free-draining rooting depth and frost exposure | Rainfall/drainage gates; orchard checks unresolved |

Sources: [NSW Winter crop variety sowing guide 2026 V2, April 2026](https://www.dpird.nsw.gov.au/__data/assets/pdf_file/0008/1664405/2026-Winter-crop-variety-sowing-guide-V2.pdf); [Macadamia grower's guide 2023: new orchards](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0011/1475984/Macadamia-Growers-Guide-new-orchards.pdf). The [remaining eight-crop review](nsw-other-crops-notes.md) records sorghum, cotton, rice, lucerne, grapes, olives, citrus and ryegrass guidance and source limitations.

## What cannot be justified yet

1. **pH comparability:** SLGA supplies pH in water, averaged over 0–30 cm. Many NSW recommendations use CaCl2 measurements and depth-specific profiles. No fixed offset, threshold substitution or automatic lime advice has been added.
2. **Texture and carbon calibration:** NSW guidance does not validate the 35% clay / 65% sand categories, 100/70/40 texture penalties, carbon curve or their weights. Carbon cannot establish nitrogen sufficiency or independently distinguish crop preferences. These remain explicitly labelled assumptions.
3. **Water and phenology:** annual rainfall cannot model water balance, reliable irrigation, or crop-stage frost/heat. Winter crop calendars depend on region, variety and purpose; broad month filters remain incomplete.
4. **Local agronomic suitability:** there is no defensible coordinate boundary here that makes a crop suitable or unsuitable everywhere on either side. Production districts and cultivar trials are not universal species exclusion maps. In particular, a high-scoring Coffs Harbour lentil is still only a conditional candidate with unresolved checks, not an endorsed planting recommendation.
5. **Other missing constraints:** salinity, sodicity, rooting depth, drainage engineering, disease/rotation, cultivar/rootstock, nutrition, markets and economics. High fire exposure remains a demo proxy, not comparative crop-damage validation. Many older guides remain useful but require current local advice.

## Validation performed and still needed

Automated cases test threshold boundaries, unknown inputs, method mismatch, drainage changes and preserved score arithmetic. These are software/guidance consistency tests, not yield-validation samples. Preset comparisons are reproducible and are not used to tune weights to expected crop names.

A credible next empirical study would obtain licensed NSW trial/field records with measured soil method/depth, climate, cultivar, management, irrigation and outcomes. Use agronomist-labelled suitability cases across coast, slopes/plains and far west; freeze rules before evaluating. Separate training/calibration and held-out sites and years. Record false endorsements, withheld viable options, sensitivity to soil uncertainty, and disagreement by crop/region. NVT variety results within a crop cannot be pooled as a universal cross-crop success label without a carefully defined endpoint. Blinded local agronomist review is required before claiming improved agronomic accuracy.

Indicative only. Check with a local agronomist.
