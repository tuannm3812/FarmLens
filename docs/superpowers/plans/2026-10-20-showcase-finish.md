# FarmLens local showcase completion plan

> **For agentic workers:** Use superpowers:executing-plans inline. Steps use checkbox syntax.

**Goal:** Finish a polished, friendly local showcase for the user's LinkedIn post on 20 October 2026.
**Architecture:** Extend the existing Python + vanilla HTML/CSS/JS app. Keep scoring separate from imagery, the report guide and the existing water/budget pilots.
**Tech Stack:** Python 3.11, pytest, node:test, Leaflet, SVG, existing OpenAI explanation client.
**Spec:** The user approved the previous five-part completion proposal, chose a local showcase only, and a friendly farming companion identity. No public deployment or social posting is requested.

## Global constraints

- Work in the existing local prototype; no commits, worktree migration or public deployment. There is no HEAD to isolate, and the user explicitly asks to finish this app.
- Keep historical plan records; make `docs/4_next_steps.md` the current status.
- Friendly field-and-sprout identity; original SVG assets, yellow/green/cream palette and existing fonts. Finn is a small report guide, not an agronomist.
- No score, yield or profit claims beyond the existing evidence. Imagery is dated context, not a health assessment.
- Keep the existing numeric-only optional OpenAI explanation path. The new report guide handles supported questions locally; typed questions stay in the browser. Clearly describe its scope.
- Meaningful behavior tests first. Visual changes use browser inspection. Run the full check command once integration is complete, then repeat affected/full checks only for fixes.

## Review focus

- A new pin or failed report must never retain the previous point's image or guide answers.
- Unknown image date/coverage must remain unknown; a failed image must not appear as a blank success.
- Report questions must not invent crop suitability, irrigation benefits, current prices or personal expertise.
- Keyboard focus, narrow layouts and source disclosures must remain usable in dialogs.
- Privacy copy must reflect actual network use; typed guide questions are local, optional model explanations remain numeric-only.

## Task 1: Standards and friendly identity

Files: `AGENTS.md`, `docs/0_coding_standards.md`, `docs/1_brief.md`, `docs/2_architecture.md`, `docs/3_decisions.md`, `docs/4_next_steps.md`, `scripts/check.py`, `.github/workflows/check.yml`, `web/assets/brand/`, existing brand icon and shared navigation/home styles.

- [x] Adopt relevant master standards with explicit app/data/palette exceptions; add one check command and CI configuration.
- [x] Create reusable friendly logo, wordmark and Finn SVG avatar; apply to shared navigation, favicon and homepage.
- [x] Record current versus historical plan status without falsely marking credential-dependent checks verified.

## Task 2: NSW imagery and concise snapshot

Files: `farmlens/imagery.py`, `web/imagery.js`, `web/companion.css`, `web/overview.js`, `web/app.js`, `farmlens/web.py`, fixture/Python/Node tests.
Interface: `ImageryClient.fetch(lat, lon, refresh=False)` returns DataResult with date-layer block metadata and point. Browser image uses a bounded NSW export at the selected point; data metadata uses the shared JSON cache. `FarmLensImagery.mount(api)` resets with `setContext(point|null)` and supports on-demand image loading.

- [x] Verify official dates/imagery response; test date parsing, malformed/missing metadata, retry/cache and precise point keys.
- [x] Build image preview, source/date disclosure, unavailable state and expanded view; avoid presenting a block date as the exact exposure of every pixel.
- [x] Test stale responses, invalid points and context reset; inspect image failure handling; simplify snapshot copy while retaining warnings.

## Task 3: Ask FarmLens

Files: `web/companion.js`, `web/index.html`, `web/app.js`, Node tests.
Interface: `FarmLensCompanion.answer(question, report)` returns a bounded, deterministic answer with source/action references. `mount(...)` owns dialog state; `setContext(report|null)` clears stale conversation. Existing numeric explanation callback remains available as an explicit action.

- [x] Test ranking/zero caps, no candidates, provisional evidence, missing factors, unsupported questions, source safety and independent water/budget scope.
- [x] Implement Finn's concise question panel with starter questions, local text matching, disclosure and clear fallback.
- [x] Preserve original OpenAI explanation feature in this panel; reset/ignore pending results on point changes.

## Task 4: Verification and share materials

Files: README, showcase poster/script, LinkedIn copy, screenshots, current status and this ledger.

- [x] Run Python and Node checks; verify live imagery for presets with cached metadata.
- [x] Browser-check home/explorer/guide/imagery, three presets, keyboard, mobile and unsupported-question fallback; document that an image-provider outage was not forced.
- [x] Fresh-context code review; fix material issues and verify.
- [x] Update local poster and script; produce a concise LinkedIn draft and share image with accurate prototype claims.
- [x] Reconcile original plan and finish checklist; leave the local showcase running.

## Execution ledger

- Ruling: user approved the completion proposal and requested execution today; no new design approval gate.
- Ruling: use the existing checkout, since all prior app work is uncommitted and no HEAD exists. Git-dependent skill helpers cannot provide meaningful task ranges; this file is the execution record.
- Ruling: guided local questions provide a reliable, credential-free assistant for the showcase; optional OpenAI wording is preserved. This is not a general conversational agronomy service.
- Pre-flight: imagery and guide both consume the selected point/report lifecycle; clear both at the start of analysis and pass data only after the matching successful result.

- Completed: relevant standards and one release command/CI configuration; friendly reusable SVG identity; shortened snapshot and official selected-point imagery; Finn local guide with optional numeric-only explanations preserved.
- Red/green evidence: imagery module/client/helper and route tests failed before implementation, then passed. Guide tests failed before implementation, then passed. New brand asset route checks exposed 404s; explicit allowlist entries fixed all three.
- Full local app verification: `python scripts/check.py` exited 0, with 305 Python tests, 43 Node tests, Python compilation and JS syntax checks. The final browser console had no errors.
- Browser: real imagery loaded for Coffs Harbour, Dubbo and Broken Hill. Survey dates were 2009-12-07, 2009-04-03 and 2013-07-24 respectively. Tested Home/Explore, guide answers, crop explanation fallback, water action, location resets, Escape/focus and narrow layout without horizontal overflow.
- Fresh review: no Critical/Important findings. One Minor multiple-block-date listing suggestion is deferred and documented; all three presets had one dated block. Reviewer independently passed 49 Python and 11 Node targeted cases.
- Verification limit: metadata/client failure boundaries were fixture-tested; image retry/unavailable handling was inspected in code, without forcing a live provider outage in the browser. No credentialed OpenAI/FIRMS or hosted CI result is claimed.
- Artifacts: new A3 landscape poster, two-page A4 script, 1200×1500 LinkedIn image and editable post draft. Render checks report loaded fonts/images, no overflow and no footer overlap. Every PDF page and final image were visually inspected. Earlier artifacts remain intact.
- Reconciliation: original plan now points to `docs/4_next_steps.md`; local showcase complete. The app remains running at port 8503. Remaining calibration, credentials and minor follow-up are in `docs/showcase/showcase-release-notes.md`.
