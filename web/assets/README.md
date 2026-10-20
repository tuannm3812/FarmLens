# FarmLens asset library

- `crops/`: 15 crop photographs and `manifest.json` with source page, creator, exact licence, source description, dimensions, download URL and SHA-256 hash.
- `icons/crops.svg`: original, reusable monochrome symbols for grain, pulses, flowers, fruit, nuts and forage. These are visual identifiers, not botanical diagrams.
- `icons/brand.svg`: FarmLens favicon / brand mark.
- Existing local Inter and Manrope fonts and their OFL licences remain in `web/fonts/`.

Photos are illustrative examples, not images of the selected point or recommended cultivars. They are served locally and requested when a crop profile opens. Their dimensions are reserved to avoid layout jumps; an icon fallback appears if a photo cannot load. The app does not contact Wikimedia at runtime.

## Photo attribution and licences

Each crop profile exposes its original file title, creator, source link and licence link under **Photo credit & licence**. The manifest is the authoritative credit inventory. Individual images retain their stated Creative Commons or public-domain status. Displayed crops and thumbnails of ShareAlike images remain under the same corresponding licence. Neither the photographers nor Wikimedia endorse FarmLens.

The JPEG bytes are Wikimedia-provided thumbnails (up to 960 px wide), or their smaller originals. The app displays them in a cropped frame with CSS; no generative edits were made. Canola shows a field near Temora, NSW. Improved pasture shows perennial ryegrass; citrus shows sweet orange. Other photos may come from outside Australia.

Three older file descriptions lack machine-readable creator fields. Their credits were verified on the linked file pages: canola — John O’Neill (edited by Fir0002); grapes — BerndtF; cotton — USDA Natural Resources Conservation Service. The refresh script preserves those overrides.

To refresh the library, run `.venv/bin/python scripts/fetch_crop_assets.py` with internet access. Optional crop IDs limit refreshes, e.g. `... canola chickpea`. Review changed photos and metadata before distribution. Runtime operation and tests need no downloads.

## Adding a crop

1. Match the photograph's source identity to the crop species/proxy.
2. Check its reuse licence and retain the exact attribution.
3. Update the script selection and manifest; visually inspect the resulting image and alt text.
4. Add the crop ID to the server's explicit static-asset allowlist and map an appropriate SVG symbol in `web/presentation.js`.
5. Keep all image paths local. Run the asset and presentation tests.

## Land snapshot visuals

- `icons/land.svg`: original monochrome symbols for six DEA Level 3 classes, an unknown class and soil texture, pH and organic carbon. Use with local SVG `<use>` references; `currentColor` follows the interface.
- `land-cover/`: original 240×144 SVG illustrations (`cultivated`, `natural`, `aquatic`, `built`, `bare`, `water`, `unknown`). No external resources, photos, scripts or fonts are embedded. Palette: FarmLens forest green, harvest yellow, muted blue and warm earth neutrals.
- `land-cover/preview.html`: local visual catalogue, available at `/assets/land-cover/preview.html` while the app runs.

These illustrations are authored for FarmLens and have no third-party image attribution requirements. They communicate the **category** returned by DEA; geometry, plants, structures and proportions are symbolic. They must never be described as imagery of the selected location, a parcel map or a live condition measurement. The current compact land card uses only the monochrome icons. These illustrations remain in the gallery for optional reuse; any future placement must label them as symbolic and keep DEA data attribution separate.

Class mapping: 111 → cultivated; 112 → natural; 124 → aquatic; 215 → built; 216 → bare; 220 → water. Missing, loading, offline and unknown classes use the neutral `unknown` icon in the current report. The gallery retains an equivalent neutral illustration.

To extend the library, draw at the same SVG viewBox, keep data-free illustrative geometry, add an explicit server asset route, and review desktop/mobile appearance. Avoid location-specific details that the source does not measure.

The homepage reuses the bundled canola image, with the Temora NSW caption and creator/licence links in its footer. No additional image downloads are needed.
# Friendly identity

The original FarmLens field-and-sprout mark lives in `icons/brand.svg`.
`brand/wordmark.svg` is the horizontal lockup; `brand/mark-mono.svg` is the
single-colour symbol, and `brand/finn.svg` is the separate illustrated report
guide. These SVG assets were authored for FarmLens. The wordmark uses Manrope
when available and falls back to Arial; web pages use the bundled licensed font.
Finn represents software guidance, not a real person or accredited agronomist.
