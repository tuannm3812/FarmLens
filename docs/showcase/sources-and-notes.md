# FarmLens showcase | sources and production notes

Prepared for Codex Builder Day, 20 October 2026. The user confirmed landscape orientation and approximately three minutes; A3 is the production default. The three-minute slot includes demo actions. The intended audience is other builders viewing the working prototype.

## Deliverables

| File | Purpose |
| --- | --- |
| `farmlens-poster-a3.pdf` | One-page A3 landscape poster, 420 × 297 mm, ready to print at actual size |
| `farmlens-poster-preview.png` | Raster preview rendered from the final PDF |
| `farmlens-poster.html` | Editable, self-contained poster: local fonts and images embedded; change text and CSS in a text editor |
| `presentation-demo-script.pdf` | Three-page presenter handout: timed pitch, screen cues and 60-second backup |
| `presentation-demo-script.md` | Editable script, fuller demo setup, recovery guidance and short Q&A |
| `presentation-demo-script.html` | Editable, self-contained print source for the presenter handout |
| `build_showcase.py` | Rebuilds HTML and Markdown sources from project assets and the saved water checkpoint |
| `render_showcase.cjs` | Prints the HTML sources to PDF using a separate temporary Chromium profile |
| `qa/` | PDF-rendered presenter pages and a verification record |
| `licenses/` | Original bundled Manrope and Inter font licences and source inventory |

The poster is a browser-editable source document, not a PowerPoint slide. Open the HTML in a browser to view or print; edit its text/CSS in an editor. To regenerate after editing `build_showcase.py`, run Python from the repository, then run the render script with Playwright available. Regeneration overwrites the generated HTML and Markdown; edit either the generator or the generated source deliberately. The final PDFs embed their fonts and require no network to display. The screenshot is raster artwork; main poster copy and chart labels remain text in the PDF.

Print the poster at **A3 landscape, 100% / actual size**, with no printer headers or footers. The design has internal margins and does not require full bleed. This is a digital/office-print PDF in RGB, not a press-specific CMYK or PDF/X production file. No public URL, QR code, author identity, university affiliation or sponsor endorsement was invented.

## Project evidence ledger

All capability statements are grounded in the existing repository, inspected during this task. No application files or existing screenshots were edited, and the shared app browser was not used.

| Claim / material | Local evidence | Qualification |
| --- | --- | --- |
| NSW point selection, public-address search, two modes, 15 profiles, transparent weights | `../../README.md`, `../../web/index.html`, `../../web/app.js` | Provisional screening, not planting advice |
| ERA5, SLGA, EcoCrop and NSW checks | `../../README.md`, `../research/2026-10-20-nsw-scoring-validation.md` | Modelled climate/soil; approximate crop ranges and uncalibrated weights |
| Water balance, coefficients and defaults | `../research/2026-10-20-water-method.md`, `../../web/water.js`, `../../data/water_profiles.json` | Separate historical pilot; does not change scores |
| Poster bars and spoken water figures | `../checkpoints/water-feasibility.md`, `../checkpoints/water-feasibility.json` | Chart values read directly from saved wheat scenarios, rounded to two decimals |
| Recorded 230 Python tests | `../../README.md`, task handoff evidence | Prior recorded run, not a new test run for poster creation |
| Recorded 11 JavaScript tests | Task handoff's last-complete-run evidence | Prior recorded run, not a new test run for poster creation |
| Live preset water histories fetched | `../checkpoints/water-feasibility.md` and JSON provenance | Three preset locations; not farm-level calibration |
| UI illustration | `../screenshots/harvest-workspace.png` | Existing recorded screenshot; some later controls differ |
| Optional demo fallback images | `../screenshots/crop-profile-assets.png`, `../screenshots/water-feasibility.png` | Existing files remain unchanged |

The original poster snapshot predates locality labels and Land overview. The updated script now includes implemented nearby locality names, Land snapshot, Seven-day weather and Seasonal climate; see the update below. The poster remains the earlier recorded showcase snapshot. OpenAI and NASA FIRMS credentialed live responses are not claimed as verified. Source documentation was read locally; the source links below were preserved from the project rather than independently re-researched for this poster.

## Water example: exact interpretation

The poster compares **median model-estimated gross irrigation to cover the accumulated net gap**, not actual irrigation supplied or a water allocation. All three chart rows use wheat, May 1 sowing, 20 / 30 / 60 / 40-day stages, 100 mm readily available soil-water buffer, 50 mm water at sowing, 80% rain infiltration and 80% irrigation efficiency. These are illustrative assumptions, not measurements or SLGA-derived water capacity.

| Preset | Median demand | Median additional net water | Median gross irrigation |
| --- | ---: | ---: | ---: |
| Coffs Harbour | 290 mm | 73 mm | 0.92 ML/ha |
| Dubbo | 255 mm | 60 mm | 0.75 ML/ha |
| Broken Hill | 366 mm | 261 mm | 3.26 ML/ha |

Ten complete May-start seasons run from 2016 through 2025. The downloaded calendar record spans 2015-2025 to support seasons crossing New Year. Daily demand is ET0 × Kc; infiltration fills a fixed store up to its limit, then demand draws it down. An earlier deficit cannot be erased by later rain. Gross irrigation is net gap ÷ efficiency, with 100 mm = 1 ML/ha. Medians are taken separately and need not add together. Historical 10th-90th percentile ranges describe this ten-season sample, not forecast or confidence intervals.

The model assumes water can arrive when needed and omits delivery constraints, evolving roots, stress response, salinity and waterlogging. Wheat and barley have identical default coefficients and timing. Canola's default timing is an explicit illustrative assumption. The next validation step is comparison with measured soil-water and locally calibrated crop-stage/ET records, reviewed with an agronomist.

## Data and method references

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): ERA5 reanalysis, historical daily rain and FAO-56 reference evapotranspiration. Modelled gridded weather, not a farm weather-station record.
- [Open-Meteo Forecast API](https://open-meteo.com/en/docs): the app's separate short-term weather context; it is not the historical water input used in this poster.
- [Soil and Landscape Grid of Australia attribute products](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html) and [CSIRO TERN map services](https://soils.csiro.au/arcgis/rest/services/TERN): CSIRO / TERN / ACLEP and collaborators, CC BY 4.0. Modelled pH in water, broad texture and carbon; the app aggregates 0-30 cm.
- [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home): approximate environmental requirements; individual species links are retained in `../../data/crops.csv`.
- [FAO Irrigation and Drainage Paper 56, Chapter 6](https://www.fao.org/4/x0490e/x0490e0b.htm): stage coefficient framework, Tables 11 and 12. These do not calibrate the pilot for NSW cultivars.
- [NSW soil moisture monitoring guidance](https://www.nsw.gov.au/regional-and-primary-industries/agriculture/soil/soil-moisture/moisture-monitoring): context for monitoring active root zones and irrigation timing; does not validate FarmLens defaults.
- Full source-linked NSW eligibility research: `../research/2026-10-20-nsw-scoring-validation.md`.

## Image, map and font credits

**Canola photo:** [Canola field temora nsw.jpg](https://commons.wikimedia.org/wiki/File:Canola_field_temora_nsw.jpg), John O'Neill (edited by Fir0002), [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). The authorised local file is `../../web/assets/crops/canola.jpg`. The poster crops its frame and resizes it; there are no generative changes. The displayed photo/crop remains under CC BY-SA 3.0. It shows an example crop near Temora, not the selected Dubbo point, and implies no endorsement. The fallback crop-profile screenshot also contains this photo. Exact inventory and original hash: `../../web/assets/crops/manifest.json`.

**Interface screenshot:** Existing FarmLens screenshot, `../screenshots/harvest-workspace.png`, embedded unchanged in content and proportion. Original pixels remain intact; the poster adds a rounded frame. Existing assets and usage notes: `../../web/assets/README.md`.

**Map:** © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL. The retained attribution is visible in the screenshot and repeated on the poster. NSW boundary: [ABS ASGS 2021 state boundaries](https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/STE/MapServer/0), CC BY 4.0, simplified by the app. It is not a parcel survey.

**Brand mark:** The existing FarmLens monochrome mark from `../../web/assets/icons/brand.svg`; no new logo or external brand mark was invented.

**Fonts:** Existing local Manrope and Inter files, embedded in the self-contained HTML and PDF. Original SIL Open Font License notices and source inventory are copied into `licenses/`. The fonts themselves are not sold or relicensed by this showcase.

Indicative only. Check with a local agronomist.

## Latest script update: Land overview and locality labels

The main talk and 60-second backup now follow the implemented interface: choose a location, inspect Land snapshot, review Seven-day weather and Seasonal climate, explore crop options, then inspect the separate water pilot. The main talk has 352 words, with one spoken sentence per line and bold memory cues. The 60-second backup has 113 words.

Evidence inspected: `../../web/index.html`, `../../web/overview.js`, `../../web/app.js`, `../../farmlens/geocode.py`, `../../farmlens/web.py`, `../research/2026-10-20-land-cover.md`, and the existing `../screenshots/land-overview.png`. The DEA land-cover source is [Geoscience Australia DEA Land Cover](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/), CC BY 4.0. The 2025 classification is historical pixel context, not farm health or a crop-score input. Forecast weather and historical seasonal patterns are kept distinct in the talk. Locality labels give nearby place context without confirming a property address.

Fresh targeted verification for this update: 27 Python cases across `tests/test_geocode.py` and `tests/test_land_cover.py`, plus 8 JavaScript cases across `tests/web_location.test.cjs` and `tests/web_overview.test.cjs`, all passed. No new shared-browser session or live provider checks were performed. README contains test counts from different checkpoints, so the talk uses “automated checks” without claiming a newly run full-suite total.

Indicative only. Check with a local agronomist.

The 60-second version now introduces Mike as a Master of Data Science student at UTS, frames the six-hour build, names intended NSW farmer/landowner users and their information-search problem, and includes a brief Dubbo demo and thank-you. Identity and build-duration wording comes from the user; intended users are product positioning, not a claim of customer research. Re-rendered and visually checked the revised page.
