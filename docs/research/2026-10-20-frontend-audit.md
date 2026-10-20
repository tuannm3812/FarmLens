# FarmLens frontend audit — 20 October 2026

Scope: component and state review of both `web/` (custom local app) and `app.py` (retained Streamlit), with fixes applied. This is a usability and evidence-presentation audit, not an accessibility certification or a field validation of the recommendations.

| Component | Finding and refinement | Verification |
| --- | --- | --- |
| Header / approach dialog | Keep monochrome identity; explain all seven weights and the new NSW eligibility layer. Distinguish screening from yield/profit prediction. | Desktop dialog inspected |
| Map / location pin / presets | Update selected name and pin while loading; rejected points cannot retain a valid-looking pin. Reset user drainage only when coordinates change. | Preset change and drainage reset checked in browser; geographic and Streamlit tests |
| Address search | Editing or changing location clears old matches and cancels obsolete requests. Add live search status, focus styling and a pre-action Nominatim disclosure. | Orange public-place search, edited-query clearing, result selection and missing-soil state checked |
| Water / category / season | Explain historical seasonal conditions and annual-rainfall scoring. Irrigation availability remains unverified. | Seasonal May scenario and methodology checked |
| Drainage | Add optional observed drainage; never infer it from sand/clay. Reset on new point. | Browser and offline scoring/API/Streamlit cases |
| Cache / loading / errors | Keep cached and stale evidence distinct. Show actionable shortlist refresh errors. No raw internal exception exposure. | API tests; cached preset and unavailable-soil browser checks |
| Summary metrics / outlook | Label pH as water, averaged over 0–30 cm; explain why it cannot substitute for CaCl2. Retain forecast dates and freshness. | Browser summary and evidence panel checked |
| Crop cards / factor bars | Collapse cards initially; label each candidate, including individually capped crops within a mixed shortlist. Show previously omitted profile notes. Increase type size/contrast; reserve room for “Unassessed”. | Dubbo expansion and Coffs Harbour mixed-strength shortlist checked; mobile factor bars inspected |
| NSW guidance details | Add source-linked checks, unknowns and conflicts. Preserve reasons for withheld crops; show exclusion count by shortlist. | Canola guidance expanded; seasonal poor-drainage exclusions inspected |
| Land & sources | Keep soil method, uncertainty, retrieval records, fire availability and exclusion details accessible. | Browser inspection and offline provenance tests |
| Report tabs / keyboard | Roving tabindex and arrow-key navigation; visible focus styles. | ArrowRight switched to Land & sources |
| Explain | Disclose OpenAI transmission before action. Keep local NSW cautions separate from model wording. Bind responses to evidence freshness, not just identical scores. | Rule fallback inspected; model privacy/caution tests and fresh-to-stale regression |
| Footer | Keep required agronomist notice legible, plus score-probability distinction. | Desktop/mobile screenshots |
| Responsive layout | Larger body/caveat text; long location names constrained; responsive cards and evidence. | 390 × 844 viewport requested, expanded card checked with no horizontal overflow; override reset |
| Streamlit parity | Add drainage, per-crop caveats, source expanders, exclusion reasons and persistent explanation cautions. | Four offline Streamlit AppTest cases passed; no new live Streamlit browser pass claimed |

## Verification record

- Full offline suite: **181 passed** (`.venv/bin/pytest -q`).
- `node --check web/app.js` and Python compilation passed.
- Independent code review found two actionable issues: freshness omitted from explanation fingerprint and missing custom-UI pre-action disclosures. Both are fixed; the freshness regression was observed failing before the fix and passing afterward.
- Custom app checked at `http://127.0.0.1:8503/`; no browser console errors were captured in the final check. Preset scenarios used cached actual source data. Search used a public town name. OpenAI and FIRMS were not tested with credentials.
- Preview: [reviewed shortlist](../screenshots/nsw-guidance-workspace.png).

## Remaining refinements worth doing next

1. The largest reliability gap is agronomic calibration: source-backed constraints improve screening, but weights and texture/carbon penalties still lack NSW outcome validation. Use blinded agronomist-labelled cases before presenting a stronger confidence claim.
2. Add crop-specific regional/varietal calendars and measured depth-specific soil inputs, with explicit units and methods. The current Coffs Harbour annual shortlist can still include conditional candidates that need local scrutiny.
3. Test with farmers on mobile and with screen-reader users. The report is deliberately detailed and still involves vertical scrolling; usage evidence should determine whether secondary controls belong in a collapsible scenario panel.
4. Replace external Leaflet/map dependencies with a deployment-appropriate asset strategy if fully offline mapping is required. Cached data mode does not make map tiles available offline.

Indicative only. Check with a local agronomist.
