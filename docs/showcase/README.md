# Product showcase

Recorded examples from the local FarmLens prototype, captured on 20 October
2026. These assets show saved results, not live data.

| Asset | Purpose |
| --- | --- |
| [Product cover](farmlens-cover.png) | README introduction; cropped Dubbo land report |
| [24-second walkthrough](farmlens-walkthrough.mp4) · [GIF](farmlens-walkthrough.gif) | Land context → crop options → factor scores → Finn |
| [Full app snapshot](../screenshots/showcase-explorer.png) | Dubbo explorer, including the soil indicators |
| [A3 poster](farmlens-showcase-2026-10-20.pdf) · [Preview](farmlens-showcase-preview.png) | Detailed project presentation |

The walkthrough is four paced screenshots with captions and focused crops of the
real interface. Its timing does not represent application speed. Finn's example
answer comes from the local report guide, without an OpenAI model call. Data and
score values have not been edited. Preset coordinates are town-centre examples,
not verified farm paddocks.

Current software check results are in
[GitHub Actions](https://github.com/tuannm3812/FarmLens/actions/workflows/check.yml).

## Credits

- **Map:** © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright),
  ODbL. NSW boundary © ABS, CC BY 4.0; simplified ASGS 2021 geometry.
- **Land imagery:** © NSW Department of Customer Service, including third-party
  imagery. [NSW Spatial Services mosaic](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer)
  and [survey-block dates](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery_Dates/MapServer).
  The recorded Dubbo block date is 3 April 2009. A block date does not certify
  the exposure of every surrounding pixel or current land conditions.
- **Modelled soil:** CSIRO / TERN / ACLEP and collaborators,
  [Soil and Landscape Grid of Australia](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html),
  CC BY 4.0.
- **Land cover:** Geoscience Australia,
  [Digital Earth Australia](https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/),
  CC BY 4.0.
- **Climate and crop references:** [Open-Meteo](https://open-meteo.com/en/docs),
  [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home) and the
  [source-linked NSW guidance review](../research/2026-10-20-nsw-scoring-validation.md).
- **Typography:** Inter and Manrope, SIL Open Font License. The PDF embeds these
  fonts, and the cover and walkthrough render them. [Sources](licenses/sources.json),
  [Inter licence](licenses/Inter-OFL.txt) and [Manrope licence](licenses/Manrope-OFL.txt)
  accompany the assets.
- **Branding:** original FarmLens logo and Finn SVG artwork. MIT covers the
  original artwork and code; third-party content retains its own terms.

The poster was rendered at A3 landscape and visually inspected. It is RGB
digital/office output, not a press-specific CMYK or PDF/X file. Reuse must retain
applicable attribution; see the repository [third-party notice](../../NOTICE.md).

Indicative only. Check with a local agronomist.
