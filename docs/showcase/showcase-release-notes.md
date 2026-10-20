# FarmLens local showcase — 20 October 2026

This is the current showcase package. The earlier poster/script remain intact
as historical artifacts. No public hosting or social posting was performed.

## Files to use today

| File | Purpose |
| --- | --- |
| `farmlens-linkedin.png` | 1200 × 1500 share image with the recorded Dubbo land overview |
| `linkedin-post.md` | Editable LinkedIn draft and suggested alt text |
| `farmlens-showcase-2026-10-20.pdf` | One-page A3 landscape poster |
| `farmlens-showcase-preview.png` | Preview rendered from the final poster PDF |
| `showcase-demo-script.pdf` | Two-page A4 presenter handout |
| `showcase-demo-script.md` | Three-minute walkthrough, 60-second backup and preparation notes |
| `build_local_showcase.py` | Rebuild the self-contained HTML from the local assets/script |
| `render_local_showcase.cjs` | Render with Playwright; no remote assets are loaded |
| `showcase-render-checks.json` | Font/image, overflow and footer-spacing checks |

The poster and script PDFs were rendered and every page visually inspected.
The social PNG was inspected at its final dimensions. Main document text remains
selectable in the PDFs; app screenshots are raster. Print the poster at A3
landscape, actual size. This is RGB office/digital output, not a press-specific
CMYK/PDF-X file.

To regenerate, run `python docs/showcase/build_local_showcase.py`, then
`node docs/showcase/render_local_showcase.cjs` with Playwright available on
`NODE_PATH`. Rendering does not publish anything or connect to the app.

## What is finished

- Relevant app conventions from the personal coding standard, documented project
  exceptions, one local check command and a matching GitHub Actions configuration.
- Original reusable logo, wordmark, monochrome mark and separate Finn avatar.
- Concise land snapshot, collapsed secondary context and official NSW imagery.
- Finn's supported local report questions and the preserved optional numeric-only
  explanation action.
- New share image, poster, script and LinkedIn draft.

## Verification

`python scripts/check.py` exited successfully: **305 pytest cases and 43 Node
cases**, plus Python compilation and JavaScript syntax checks. All automated
tests use fixtures or local computations; no live network is required.

The new coverage includes imagery date parsing, retry/cache behavior, malformed
metadata, point precision and stale responses; guide zero caps, absent candidates,
missing factors, unsupported questions and safe source links; and explicit brand
asset routes. The original model explanation was also exercised in the browser
through its no-key fallback.

The final code review found no Critical or Important issues in the additions.
Its one minor follow-up is below. The reviewer independently passed 49 targeted
Python and 11 JavaScript cases.

Browser checks covered Home/Explore navigation, desktop and approximately
390-pixel mobile layouts without horizontal overflow, Finn's fallback and water
action, Escape returning focus, crop profile explanations, and conversation
reset on location change. Real imagery loaded for all three presets. The selected
point's image clears before replacement. Image-error handling was inspected in
code; a real provider outage was not forced during the browser run.

The forecast and soil values shown in screenshots retain their source/cache
labels. A screenshot is a recorded example, not a fresh request when viewed later.
The local server was left running at port 8503. Hosted CI and credentialed
OpenAI/FIRMS calls were not verified in this release.

## Image and data credits

The release uses original SVG brand/guide assets from `web/assets/brand/` and
`web/assets/icons/brand.svg`, plus the existing Inter and Manrope fonts (SIL OFL;
see `licenses/`). New screenshots are in `docs/screenshots/showcase-*.png`.

- Map © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright),
  ODbL; NSW boundary © ABS, CC BY 4.0.
- Land imagery © NSW Department of Customer Service, including third-party
  imagery. [NSW Spatial Services mosaic and attribution](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer)
  and [survey-block metadata](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery_Dates/MapServer).
  The recorded Dubbo block date is 3 April 2009; Coffs Harbour is 7 December 2009
  and Broken Hill is 24 July 2013. Dates do not certify the exposure of every
  surrounding pixel or current conditions.
- Modelled soil © CSIRO/TERN/ACLEP and collaborators,
  [SLGA](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html),
  CC BY 4.0.
- Land cover and fractional cover © Geoscience Australia,
  [DEA](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/),
  CC BY 4.0.
- Climate and forecast: [Open-Meteo](https://open-meteo.com/en/docs).
  Crop profiles: [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home).
  Source-linked NSW checks and water/budget references are documented in the
  main README and `docs/research/`.
- The separate homepage screenshot contains the example Temora canola photo by
  John O'Neill, edited by Fir0002,
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
  It is an example crop, not the selected land. See the existing
  `sources-and-notes.md` and photo manifest for the original source.

## Deferred after the local showcase

One minor presentation follow-up: when several imagery blocks with different
dates intersect the pin, the interface says “Multiple survey dates” and links
the official source, but does not yet list every returned block date in the
expanded view. All three demo pins returned one dated block.

Longer-term work remains agronomist-labelled validation and calibration, measured
soil-water comparisons, operational hosting and credentialed live integrations.
The scores and pilots are not validated yield, irrigation or profit forecasts.
Finn is a report companion, not an agronomist.

Indicative only. Check with a local agronomist.
