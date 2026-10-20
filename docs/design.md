# FarmLens product design

This reference describes the current local showcase and the conventions to
preserve when editing it. It is not a record of discarded designs or a claim
that the product has been validated with farmers.

## Purpose and voice

Help someone explore a NSW location, compare crop candidates and understand
the evidence and uncertainty behind the shortlist.

The brand is a friendly farming companion: calm, practical and specific.
Lead with the result, then the reason and the next local check. Prefer
“crop options” and “screening score” to promises about the best crop or yield.
Finn is an illustrated software guide, not an accredited agronomist.

## Pages and information order

| Surface | Job |
| --- | --- |
| Home | Explain the purpose and invite the visitor to explore land |
| Explore land | Select a point, inspect its context and compare crop options |
| How it works | Explain sources, screening logic and limitations |
| Shared navigation | Keep these three destinations and FarmLens identity consistent |

In Explore, keep the map beside the report on desktop. On narrow screens,
stack the content and retain the map visibility control. Public-place search
and the three presets provide alternatives to clicking the map.

The report leads with location, land snapshot and seven-day weather, followed
by growing scenario and crop options. Seasonal climate, vegetation history,
water scenarios, budgets and cross-crop comparison open on demand.
The **Data & sources** tab holds detailed evidence and status.

## Visual foundations

Use the existing tokens in [`web/style.css`](../web/style.css).
Component styles extend them; this document does not define a second theme.

| Token | Value | Role |
| --- | --- | --- |
| `--green` | `#355B48` | Brand, crop identity and stronger screening states |
| `--yellow` | `#E7B83C` | Primary actions, selected location and highlights |
| `--wash` / `--paper` | `#F7F4EB` / `#FFFFFF` | Page and card surfaces |
| `--ink` / `--muted` | `#252A26` / `#62665D` | Main and supporting text |
| `--blue` | `#316B83` | Links and weather/water context |
| `--rust` | `#A5442D` | Constraints and factors to watch |
| `--line` | `#DEDACD` | Quiet borders and separators |

Manrope is used for headings and brand text; Inter for body copy, controls and
data. Both fonts are bundled locally. Reuse the established rounded cards,
thin borders and restrained shadows. Colour supports a text label or number;
it must not be the only way to understand a state.

Use original monochrome crop and land icons for quick recognition. Keep the
FarmLens mark primary and Finn secondary. Crop photographs are examples,
not photographs of the selected point. Asset paths, credits and reuse rules
are in the [asset inventory](../web/assets/README.md).

## Component decisions

| Component | Presentation rule |
| --- | --- |
| Land snapshot | Land-cover class, soil texture, pH and organic carbon; keep units, modelled depth and source status accessible |
| Soil indicators | Show composition or position on a scale, not a red-to-green soil-health grade; pH 7 is neutral, not a universal crop target |
| Land imagery | Show the source survey date and attribution; never imply a live image or infer ownership and drainage |
| Weather | Seven dated daily values with simple symbols; keep forecast and historical climate distinct |
| Crop shortlist | Up to three candidates, score out of 100, crop tags, one fit reason and the weakest assessed factor |
| Crop profile | Example photo, clear limitation, factor bars and supporting source links |
| Crop comparison | Optional radar for the overall pattern, with numeric values available; gaps mean unassessed, not zero |
| Water and budget | Separate editable scenarios; water shortfall is not verified supply and gross margin is not net profit |
| Ask FarmLens | Suggested questions first; local report answers, with optional model explanations clearly separated |

Keep essential qualifications beside the result. Put longer methods, definitions
and provenance in an expander, profile or source tab. Decorative land-cover
illustrations remain in the asset gallery; the compact report uses icons and
dated imagery.

## Interaction and evidence

- Clear old location-dependent results when a new point is selected. A late
  response must not restore the previous location's report.
- Distinguish loading, cached, stale, unavailable, unassessed and measured zero.
  Do not draw a scale marker or assign a score to missing evidence.
- Preserve visible keyboard focus, labelled controls, dialog close actions,
  status announcements and reduced-motion behaviour. Check desktop and narrow
  layouts after visual changes; this is a review checklist, not a certification.
- Keep Finn's typed questions local. The separate optional OpenAI action uses
  only the numeric allowlist; see [architecture](2_architecture.md).
- Keep scores provisional. Forecast, imagery, vegetation, water scenarios and
  budgets do not change crop rankings. End advice with:
  “Indicative only. Check with a local agronomist.”

For calculations and unresolved agronomic checks, use
[Methods and limitations](technical-reference.md). The
[product showcase](showcase/README.md) contains the current visual examples.
