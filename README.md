<p align="center">
  <img src="web/assets/icons/brand.svg" width="72" alt="FarmLens logo">
</p>

<h1 align="center">FarmLens</h1>
<p align="center"><strong>Your land, your climate, your best crops, with the reasons.</strong></p>
<p align="center">A friendly farming companion for exploring land in New South Wales.</p>
<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&amp;logo=python&amp;logoColor=white" alt="Python 3.11"></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="https://img.shields.io/badge/JavaScript-ES%20modules-F7DF1E?style=flat&amp;logo=javascript&amp;logoColor=white" alt="JavaScript ES modules"></a>
  <a href="https://leafletjs.com/"><img src="https://img.shields.io/badge/Leaflet-Maps-199900?style=flat&amp;logo=leaflet&amp;logoColor=white" alt="Leaflet maps"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-Optional%20UI-FF4B4B?style=flat&amp;logo=streamlit&amp;logoColor=white" alt="Streamlit optional UI"></a>
</p>

FarmLens brings climate, Australian modelled soil and crop requirements into one
map-led report. Choose a point in New South Wales, compare up to three crop candidates,
and inspect the reasons and limitations behind each score.

**Status:** working local showcase. There is no public interactive demo yet.
Scores are provisional screening indices, not planting advice, yield forecasts
or probabilities of success.

![FarmLens explorer showing the Dubbo land snapshot, dated imagery and weather](docs/screenshots/showcase-explorer.png)

*Recorded Dubbo example. Source dates and data status remain visible in the report.*

## What you can explore

- **Your land:** drop a pin, search a public address or try Coffs Harbour, Dubbo
  and Broken Hill. Nearby place labels help identify the area.
- **Climate and soil:** ten complete years of climate, a separate seven-day
  forecast, and modelled 0–30 cm soil pH, texture and organic carbon.
- **Crop options:** 15 sourced profiles, transparent factor scores, weakest
  factors and source-linked NSW guidance checks.
- **Land context:** dated NSW aerial/satellite imagery, DEA land cover and
  on-demand vegetation cover observations.
- **Water and budgets:** separate scenarios for wheat, barley and canola, with
  editable assumptions. Gross margin is not net profit.
- **Ask FarmLens:** Finn answers supported questions about the current report
  locally. Optional OpenAI crop explanations use only approved numeric inputs.

The custom frontend has Home, Explore land and How it works pages. The original
Streamlit interface is also retained.

## Run locally

Use Python **3.11**. Node.js **22** is needed for frontend tests, not to run the app.

```sh
git clone https://github.com/tuannm3812/FarmLens.git
cd FarmLens
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m farmlens.web
```

Open **http://127.0.0.1:8503/**. On Windows, activate with
`.venv\Scripts\Activate.ps1` in PowerShell. Run commands from the repository root;
use the editable install above because the app reads the bundled `web/` and `data/`
folders. This repository is not a standalone wheel distribution.

For the original Streamlit version:

```sh
streamlit run app.py
```

### Prepare a smooth demo

```sh
python scripts/warm_cache.py --skip-fire
```

This fetches real provider data for the three presets and may take several minutes.
For a focused imagery metadata refresh, use `--imagery-only`. The optional
vegetation history uses `--vegetation-only`.

Caches are deliberately excluded from Git. On a fresh clone, turn off
**Cached data only** under **About these inputs & data**, or warm the caches first.
Unavailable inputs remain labelled; the app may withhold a shortlist rather than
invent missing soil measurements. Browser map tiles and imagery can still need
internet in cached mode. The preset coordinates are town-centre examples, not
verified farm paddocks.

## Optional configuration

The main climate, Australian soil and imagery paths need no API key. Use
[`.env.example`](.env.example) as a template; the app reads shell environment
variables and **does not automatically load `.env`**.

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` and `OPENAI_MODEL` | Optional model-written crop explanations; both required, otherwise local wording is used |
| `FIRMS_MAP_KEY` | Optional NASA FIRMS fire history; missing or incomplete data stays unassessed |
| `NOMINATIM_USER_AGENT` | Application/contact identifier for address and nearby-place lookup |
| `FARMLENS_CACHE_DIR` | Optional local cache directory |

Never commit keys or personal farm information. Guide questions stay in the
browser. The separate model explanation action sends numeric crop/report inputs,
not addresses, coordinates, crop names or the guide conversation. Provider
requests for selected-point data necessarily use location coordinates.

## How the scoring works

Temperature, rainfall and pH score 100 within each crop's approximate preferred
range, decreasing linearly to zero at the absolute limits. Frost and fire use
explicit demo classes. Texture uses broad preference groups; organic carbon is a
small shared soil-condition proxy. A zero in any assessed factor caps the total
at 20. Missing factors remain unassessed and their weights are excluded.

Weights are centralized in [`farmlens/config.py`](farmlens/config.py). NSW guidance
adds source-linked constraints and unresolved local checks. The data dictionary
records every approximation in [`data/README.md`](data/README.md).

**Limits to keep in mind:** soil is modelled, imagery is dated, crop ranges and
weights are uncalibrated, and scenario inputs are not farm measurements. The
seven-day forecast, imagery, vegetation, water pilot and budgets do not change
crop rankings. Current crop prices and farm-specific yields are not predicted.

## Data sources

| Source | Used for |
| --- | --- |
| [Open-Meteo](https://open-meteo.com/en/docs) | Historical climate, forecasts and water-pilot weather |
| [CSIRO / TERN Soil and Landscape Grid of Australia](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html) | Modelled soil pH, sand, clay and organic carbon |
| [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home) | Approximate species requirements |
| [NSW agronomy references](docs/research/2026-10-20-nsw-scoring-validation.md) | Local constraints and checks |
| [NSW Spatial Services](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer) | Aerial/satellite mosaic and survey-block dates |
| [Geoscience Australia DEA](https://knowledge.dea.ga.gov.au/) | Land cover and vegetation observations |
| [OpenStreetMap / Nominatim](https://nominatim.org/) | Map context, address search and nearby locality |
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/) | Optional historical fire detections |

SoilGrids remains as an earlier tested client; SLGA is the active Australian soil
source. Water coefficients, archived budget examples and provenance are described
in [Methods and limitations](docs/technical-reference.md).

## Check and contribute

```sh
python scripts/check.py
```

This runs Python compilation, pytest, JavaScript syntax checks and Node tests.
Tests use saved fixtures and block live HTTP requests. [GitHub Actions](https://github.com/tuannm3812/FarmLens/actions/workflows/check.yml)
runs the same command. See [CONTRIBUTING.md](CONTRIBUTING.md) for development and
evidence rules, and the [architecture](docs/2_architecture.md) for the app's structure.

```text
farmlens/   Python clients, scoring, scenarios and local API
web/        Custom interface, original SVGs, licensed photos and fonts
data/       Crop profiles, source records and NSW boundary
tests/      Python/JavaScript tests and fixtures
scripts/    Cache warming, checks and demo utilities
docs/       Architecture, methods, source references and showcase poster
app.py      Retained Streamlit interface
```

## What comes next

The next substantive milestone is agronomist review and comparison with measured
field data. Public hosting needs a production deployment design: the current
server deliberately binds to localhost and rejects remote origins. Do not expose
it through a tunnel as a public service.

## Project poster

[![FarmLens project poster: land context, transparent crop scores and Finn the report guide](docs/showcase/farmlens-showcase-preview.png)](docs/showcase/farmlens-showcase-2026-10-20.pdf)

[Open the A3 poster (PDF)](docs/showcase/farmlens-showcase-2026-10-20.pdf) ·
[Image and poster credits](docs/showcase/README.md)

The poster records the 20 October 2026 showcase; its test counts describe that
snapshot. Use GitHub Actions above for current software checks.

## Licence and credits

Original code and original FarmLens SVG assets are available under [MIT](LICENSE).
Third-party photos, fonts, data and imagery retain their own terms; see
[NOTICE.md](NOTICE.md) and the [asset inventory](web/assets/README.md).

**Indicative only. Check with a local agronomist.**
