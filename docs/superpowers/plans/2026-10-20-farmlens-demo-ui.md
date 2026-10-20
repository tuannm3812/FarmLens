# FarmLens demo UI implementation plan

> Execute inline with the planning, test-driven development and verification skills; request an independent review at completion.

**Goal:** Finish the approved Streamlit demo, preserving provisional evidence and the two-mode scoring backend.

**Architecture:** `app.py` composes the sidebar, Folium map, summary, crop cards and explanations. Small package modules own location validation, data loading, explanations and optional geocoding/fire clients. Existing point caches remain the data boundary.

**Tech stack:** Python 3.11, Streamlit, Folium/streamlit-folium, pandas, requests, OpenAI SDK, pytest.

**Spec:** Original user request; approved research and step-2 checkpoint in `docs/research/2026-10-20-product-and-data-review.md` and `docs/checkpoints/step-2.md`.

## Decisions
- Continue in this user-requested repository, preserving all step-1/2 work. No publishing or external messaging.
- Sidebar presets, mode, planting month, crop category and irrigation; map and summary above three cards. Green/cream visual theme, legible data and restrained styling.
- Keep point precision in the pin; API caching uses rounded coordinates. Validate NSW locally with a sourced ABS polygon, excluding ACT. Bundle outline so map interaction survives tile/network failure.
- Provide cached demo mode and an explicit refresh; failed calls cannot silently acquire live labels. Keep missing forecast and fire unknown.
- Explanations send only anonymous crop indices and numeric inputs/sub-scores, no names, addresses or coordinates. Use `OPENAI_MODEL` only when configured, otherwise rule-based text. Fix disclaimer locally. Validate model schema and fall back on timeout, refusal or malformed output.
- Nominatim: explicit form submission, Australia restriction, application User-Agent, process-wide 1-second spacing, query-hash JSON cache (coordinates cannot key an unresolved address), no invented geocode fallback, configurable endpoint.
- FIRMS: last three complete calendar years of one sensor's standard-product detections within 25 km. Five-day requests as documented; cache validated chunks as JSON. Never classify partial coverage as low exposure. No key means exactly “fire data not configured”. Uncalibrated count thresholds and satellite limitations disclosed. Expensive first load stays explicit; warm-cache can prefetch it.

## Tasks
- [x] Add failing tests for NSW acceptance/exclusions, UI preset changes, offline badges, seasonal abstention and no-strong-match cards; implement `location.py`, `service.py`, `app.py`, theme and bundled boundary.
- [x] Add explanation tests for numeric-only payload, no-key fallback, low-match wording, timeout/malformed response fallback and exact disclaimer; implement `explain.py` and Explain button.
- [x] Add saved geocoding fixture tests for NSW filtering, empty results, retry/cache and network failure; implement `geocode.py` and sidebar form.
- [x] Add saved FIRMS fixture tests for distance/date filtering, complete-window coverage, no-key handling, malformed data and cached failure; implement `fire.py`, optional UI load and cache warming.
- [x] Run full offline pytest suite, inspect the browser UI and exercise the map, presets, scenarios and explanation fallback. Request independent review and fix consequential findings.
- [x] Update README/env vars, show a running local demo and report verified behavior and remaining data limits.

## Review focus
- A persistent map event must not overwrite a newly selected preset; location/scenario changes must clear old explanations.
- Unknown data must not become zero detections, perfect scores or a fabricated weekly forecast.
- API failures and invalid credentials must not expose secret URLs or crash rendering.
- Prompt payload cannot include free-text location or address data.
- No-strong-match and fewer-than-three results must remain visible and correctly explained.

## Progress
Plan recorded after user approved continuing beyond step 2. Network access for downloading the static ABS boundary was approved by automatic review.

## Completion evidence

- Full offline suite: 112 tests passed, including fixture API clients, map boundary, Streamlit interactions, explanations, freshness revalidation and fire request-budget regressions.
- Independent review found session-held forecast freshness and FIRMS timeout budget gaps. Both reproduced and fixed; SOURCE_TTLS is shared by clients and session freshness checks, and remaining fire deadlines constrain request timeouts and retries.
- Browser verified: public Orange NSW search and selection, arbitrary NSW map click, preset replacement, Broken Hill no-strong-match plus rule-based explanation, and Dubbo May seasonal shortlist.
- Live Nominatim test returned two Orange NSW results. OpenAI and FIRMS credentials are not configured, so their network contracts were verified with fixtures; no paid model request was made.
- Local preview runs at http://127.0.0.1:8502 (8501 was occupied). Screenshot: docs/screenshots/seasonal-shortlist.jpg. No public deployment or git commit.
- Ruling: keep execution in the original repository as requested; preserve all earlier uncommitted files.
- Ruling: initial cached demo mode is explicit; a new checkout needs cache warming for real climate. Missing soil remains offline and provisional.
- Ruling: the fire budget constrains start/retry and connection/read inactivity timeouts, not an absolute wall-clock cutoff under a continuously streaming server response; this limit is documented.
