# Soil scoring and custom local UI implementation plan

User requested texture and carbon in scoring, and chose a custom app locally first with the existing Python engine and map-led layout. Use Sites local workflow; no hosted deployment or new framework build is needed.

## Scoring

- Preserve the five existing factors and cap rule. Scale their weights by 0.8; add texture 0.15 and carbon condition 0.05. Missing factors are unassessed and renormalized.
- Record optimal and tolerated texture classes verbatim from each of 15 FAO EcoCrop species sheets (verified 20 October 2026). Wide covers mineral classes. Use the existing broad SLGA proxy: clay >=35% heavy; otherwise sand >=65% light; otherwise medium. This is explicitly a demo grouping, not a USDA classification (SLGA sand uses a different particle-size convention). No organic-soil classification from SOC alone.
- Texture ratings 100 preferred, 70 listed as tolerated, 40 not listed. These numerical penalties are FarmLens assumptions. An omitted class is not proof of an absolute biological limit and does not trigger the zero cap.
- SOC g/kg / 10 -> %. Shared, small condition factor interpolates points (0%,50), (0.8%,70), (1.5%,90), (2%,100); saturates at 100. This is an uncalibrated demo curve informed by the direction of FAO GAEZ nutrient-availability assessment and NSW's general 2% reference. It is not crop-specific nutrient sufficiency, a carbon target, or a yield response. Depth is the modelled 0–30 cm screen. No fertilizer or management bonus. Disclose assumptions visibly.
- Reject invalid/inconsistent fractions; absent factors stay null; a missing critical pH still withholds rankings. Surface carbon and texture reasons in both UIs and explanations. Preserve anonymous numeric-only OpenAI payloads.

## UI and server

- Create a custom local HTML/CSS/JS app under web/, served with a loopback-only Python HTTP server (`python -m farmlens.web`, port8503). Reuse Python clients, scoring, geocoder, explanation, boundary and optional FIRMS. Keep Streamlit available.
- Build a full-height map workspace, compact top search/presets, a scrollable results panel, expandable crop detail and source evidence, monochrome icons, responsive stacked mobile layout. Preserve rainfed/irrigated, seasonal month, category, cache-only/fresh selection.
- Validate all API requests, bound body size and timeouts, same-origin JSON POSTs, no arbitrary filesystem serving, no secrets in frontend. Prevent old asynchronous responses from replacing a newer selection.
- Use official Leaflet 1.9.4 with integrity hashes and OSM attribution. Handle mapping-library failure with a usable preset/search interface and message.

## Execution and validation

- [x] Add failing soil-factor, score integration and payload tests; implement and run regressions.
- [x] Add API contract tests, implement server and frontend.
- [x] Compare three presets and contrasting synthetic soil scenarios; record limitations.
- [x] Verify browser interactions/responsiveness, fix review findings, capture screenshots, document launch commands.

Sources: existing EcoCrop row URLs; https://www.dpi.nsw.gov.au/about-us/services/laboratory-services/soil-health/interpret ; https://gaez-v4-data.fao.org/data/documentation/GAEZ%20v4%20Model%20Documentation.pdf (soil ratings section, pp90–92); https://soilcrc.com.au/resources/amendments-to-improve-the-productivity-of-sandy-soils-fact-sheet/ (sandy-soil amendment responses are not transferable crop suitability thresholds).

Completed validation: 164 offline pytest tests; JavaScript syntax and Python compilation; desktop/mobile browser checks; address selection; map-click missing-data abstention; source profiles; seasonal controls; numeric-only rule-based explanation. Review fixes include stale search responses, preset recentering and shortlist fingerprints. Browser QA also isolated icon CSS from Leaflet boundary SVGs. See docs/checkpoints/soil-scoring-v2.md.
