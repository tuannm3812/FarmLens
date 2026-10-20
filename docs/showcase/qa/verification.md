# Showcase verification

- Rendered the final poster to a one-page A3 landscape PDF (1191.12 × 841.92 points, Chromium page-size rounding).
- Rendered the presenter handout to three A4 pages.
- All embedded images loaded and local fonts reported loaded.
- Browser layout checks found no horizontal overflow in text, flow steps or chart rows.
- Inspected the PDF-rendered poster PNG and all three handout page PNGs: no clipped or overlapping copy, missing images or broken glyphs.
- Chart values were sourced programmatically from the saved water checkpoint and displayed with a common zero-to-four ML/ha scale.
- Three-minute speech: 352 words; 60-second backup: 113 words. Timing still requires a human rehearsal.
- PDF rendering used a new temporary headless-browser profile and did not touch the shared application browser.
- Poppler emitted Type 3 glyph bounding-box warnings for the poster; visual inspection found no visible glyph defects. The handout rendered without warnings.
- Application tests were not rerun for this documentation-only work. Test counts are labelled as the recorded prior verification run, not current agronomic validation.

Indicative only. Check with a local agronomist.

## Conversational script revision

Replaced the three-minute speech with plain language, linking sentences and bold memory cues. Each spoken sentence has its own line. Re-rendered the three-page PDF; browser checks found no horizontal overflow, including the sentence lines. The 60-second backup and poster are unchanged.

## Latest-status script update

Updated the main talk, backup, demo setup and screenshot cues for Land overview, satellite land-cover context, daily weather, seasonal charts and nearby locality labels. Targeted verification passed 27 Python and 8 JavaScript cases. Re-rendered three PDF pages with fonts loaded and no horizontal overflow. Application code and the existing screenshots were not edited. The poster remains the earlier recorded snapshot.

The 60-second version now introduces Mike as a Master of Data Science student at UTS, frames the six-hour build, names intended NSW farmer/landowner users and their information-search problem, and includes a brief Dubbo demo and thank-you. Identity and build-duration wording comes from the user; intended users are product positioning, not a claim of customer research. Re-rendered and visually checked the revised page.
