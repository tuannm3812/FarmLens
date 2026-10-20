# Crop profile assets and clarity — implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Apply the UI refinements discussed with the user, including example photos for all 15 crop profiles and a reusable local asset library.
**Architecture:** Keep the existing Python server and vanilla JS frontend. Add a curated crop manifest, bundled photos and SVG symbols under web/assets; use a small presentation module for shared labels and score states.
**Tech Stack:** Python 3.11, JavaScript, HTML/CSS, pytest, Node test runner.
**Spec:** Approved in the preceding chat: visible independent scenario filters, two modes, lifecycle/use tags, coloured screening scores, plain soil context, weather context, bars plus optional radar, one correctly identified licensed photo per profile.

## Global constraints
- Keep rankings, weights, zero-cap behavior and NSW guidance intact. Carbon remains explicitly experimental in score details, not a headline fertility grade.
- Water controls explain the current rainfall-based screen. Do not add nonfunctional volume inputs or claim seasonal budgeting exists.
- Crop photos are examples, not photographs of the selected land. Preserve creator, source, licence and modification records. Load locally only when a profile opens; fallback to crop icon on error.
- Keep external attribution visible and accessible. All content remains usable without photos or optional metadata.
- Do not derive current drought or weather safety from a historical annual average.
- Static serving uses an explicit allowlist and denies traversal. No new runtime dependencies.

## Review focus
- Missing photos or manifest must not block analysis or leave a broken image.
- Unknown, capped, stale and weak scores must retain their meaning independently of colour.
- Narrow layouts and long proxy crop names must not overflow or hide tags/controls.
- Mode switches and point changes must retain/reset existing scenario state correctly.
- Every asset must match the crop identity and carry its exact source licence; no directory-wide arbitrary file serving.

### Task 1: Bundled crop assets
- [x] Source 15 images with Wikimedia metadata, inspect them, and record licences/attribution in web/assets/crops/manifest.json.
- [x] Build consistent original crop SVG symbols and reusable brand mark in web/assets/icons.
- [x] Add an explicit asset registry in farmlens/web.py with tests for allowed photos, MIME types and traversal rejection.
- [x] Document assets and reproducible download script, with runtime-free loading.

### Task 2: Clear presentation and controls
- [x] Add web/presentation.js and meaningful tests for capped/unknown scores, missing weather and safe asset metadata rendering.
- [x] Expose two mode buttons and independent water/crop/drainage filters. Explain crop lifecycle and current water screen in progressive detail.
- [x] Add crop tags, score colours, photo profile, plain texture/carbon panels and contextual factor bars. Keep radar secondary.
- [x] Label historical cards by period; add forecast summaries with transparent frost/heat thresholds and data freshness.

### Task 3: Verify and finish
- [x] Run pytest, Node tests and JavaScript syntax checks.
- [x] Check the app in browser: desktop/mobile, presets, filters, photo attribution/failure fallback, Explain and comparison.
- [x] Fresh review of changed code; resolve material findings, update README and completion ledger.

## Rulings and progress
- User authorizes implementing the designs already discussed. No additional approval checkpoint needed.
- Repo has no HEAD and all files are untracked. Continue in the current authorized prototype checkout; no unsolicited initial commit/worktree.
- Presentation/CSS is verified visually; add tests for asset security and data interpretation, not CSS implementation mirrors.
- Seasonal water demand remains a separate feature. This pass shows what the existing irrigation setting actually does.

## Completion ledger
- Added 15 bundled, visually reviewed Wikimedia JPEGs with exact creator/source/licence records and SHA-256 hashes; original monochrome SVG crop symbols and favicon; reproducible refresh script and asset documentation.
- Kept the existing ranking engine intact. Visible modes/scenarios, crop tags and score states, contextual weather, crop photos and plain soil panels are implemented.
- Review finding resolved: shortlist buttons now reference their score and summary with `aria-describedby`, retaining score state, lifecycle/use and weakest-factor context for assistive technology.
- Clarified unavailable forecast heading instead of calling it a saved outlook.
- Fresh verification: 188 offline pytest cases and 7 Node cases pass; JavaScript syntax checks pass. All 15 JPEG hashes/decoding/manifest crop IDs verified (3.21 MB total).
- Browser verification: desktop and 390×844 mobile, image credits, Escape/focus restoration, seasonal controls, water explanation, drainage exclusions/reset, all three presets, rule-based Explain, optional radar and no horizontal overflow. Missing canola photo shows fallback and restoration loads correctly. Final browser console has no errors/warnings.
- No scoring recalibration, live credentialed OpenAI/FIRMS validation or irrigation water-budget model is claimed. No public deployment or commit created.
- Saved `docs/screenshots/crop-profile-assets.png` and `docs/screenshots/crop-assets-workspace.png`; updated the README.
