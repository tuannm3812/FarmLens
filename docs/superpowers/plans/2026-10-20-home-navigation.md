# FarmLens homepage and shared navigation

> **For agentic workers:** Use superpowers:executing-plans; steps use checkbox syntax.

**Goal:** Build a concise homepage, an explanation of the method, and shared navigation connecting both to the existing explorer.
**Architecture:** Three local server-rendered HTML pages use one navigation partial and shared CSS. The existing API and vanilla-JS explorer remain intact. Session storage restores the last successfully assessed point and scenario in the same tab; named preset hash links intentionally override it.
**Tech Stack:** Existing Python HTTP server, HTML/CSS/JS, pytest and node:test. No new dependencies or hosted services.
**Spec:** User requests “help to build homepage and shared navigation also”, following the request to remove unnecessary content. Design call: Home `/`, Explore land `/explore`, How it works `/about`. Homepage offers a clear explorer entry and three preset links. Remove the decorative land illustration from the report while retaining observed classification, date, source, monochrome icon and warnings.

## Global constraints
- Local app on 127.0.0.1:8503. No publication, commits or worktree migration: current checkout is the user's authorized prototype and has no HEAD.
- Use the existing cream, harvest yellow, green and blue palette, Inter and Manrope. Reuse the credited local Temora canola photograph; no invented metrics or endorsements.
- No chatbot or voice features in this task. Preserve scoring and independent financial/water calculations.
- Only the explorer loads selected-point APIs. Home and method pages work without JavaScript.
- Same navigation on each page, current-page semantics, keyboard focus, responsive layout. Detailed report evidence remains in the report.

## Review focus
- Direct loads, reloads, browser back and preset links must reach the right page and location.
- Returning from Home/method must preserve the last valid point and scenario, without saving personal searches, financial assumptions or API keys.
- Malformed/unavailable session storage must not block the explorer. Stored coordinates still undergo server NSW validation.
- Route allowlisting and static traversal protection remain intact; all navigation works without JS.
- Mobile layout, focus and legibility; dated source caveats and built/water classifications remain visible.

## Task 1: Page routes and shared shell
Files: farmlens/web.py, web/navigation.html, web/home.html, web/about.html, web/site.css, web/index.html, tests/test_web.py.
Interface: render_page(filename, active) -> bytes; Handler serves only fixed `/`, `/explore`, `/about` routes, with trailing-slash aliases, shared navigation rendered with aria-current. `/index.html` is an explorer compatibility alias.
- [x] Add failing handler tests for page identity, a single current nav item, meaningful links and static route restrictions.
- [x] Implement shared shell, homepage and method page. Home: pitch, explorer CTA, credited canola photo, three concise steps, three demo choices. Method: how scores work, source catalogue and clear limits. Navigation has Home / Explore land / How it works.
- [x] Serve CSS/module via explicit allowlist, preserve API behavior, run handler suite.

## Task 2: Explorer integration and simplification
Files: web/navigation.js, web/app.js, web/index.html, web/overview.js, web/overview.css, tests/web_navigation.test.cjs, tests/web_overview.test.cjs.
Interface: FarmLensNavigation.read(raw,presets,hash) returns a validated selection or null; encode(point,scenario) emits only whitelisted point/scenario fields. App reads inside try/catch, saves after successful analysis. `#dubbo`, `#coffs-harbour`, `#broken-hill` select fresh preset defaults and consume the hash.
- [x] Add failing tests for round-trip selection, named-preset precedence, malformed JSON and invalid numeric/enum fields; update existing illustration test to require icon/classification/warnings.
- [x] Implement restoration, current scenario controls, shared shell and removal of decorative illustration. Keep How scoring works modal accessible from the report's methodology button.
- [x] Run Node suite and full pytest suite.

## Task 3: Review, browser checks and documentation
Files: README.md, docs/screenshots/, this plan.
- [x] Restart local server. Verify homepage, each nav path, preset launches, back/reload, retained selection and compact snapshot; desktop and 390px mobile layouts.
- [x] Fresh review of changed files; fix material issues with meaningful regressions. Run full suites and JS syntax checks.
- [x] Record screenshots and update README routes, session behavior and limits. Leave homepage and explorer available in the browser.

## Execution notes
- Ruling: Execute directly in the current local checkout under the user's explicit build request. Retain plan history here; Git-dependent execution helpers cannot run without HEAD.
- Ruling: Defaults and scope are supplied in commentary; use the existing Python server rather than creating another frontend or deploying a Site.

- Tasks 1–3 complete: page-route tests observed failing before implementation; selection tests observed missing module, then passing. Full suite: 293 Python / 32 JS.
- Fresh review found complete geocoding labels entering session storage. Fixed with a failing-then-passing regression: encode stores only a generic name; read reconstructs known preset names from coordinates and sanitizes legacy labels. No other Critical/Important findings.
- Browser evidence: Coffs Harbour and Broken Hill homepage launches, Dubbo mobile launch, explicit preset resets, reload and back, return from method retaining water/drainage, scoring modal, and no horizontal overflow on 390px homepage/method/explorer.
- Local shared shell, no new dependencies or deployment. Retained existing illustration assets but removed them from the card.

- Final artifacts: docs/screenshots/homepage.png (full page), homepage-mobile.png and explorer-navigation.png. Targeted page-route tests pass after final copy refinement. Shared navbar, method and explorer mobile views have no horizontal overflow; explorer console has no errors. Homepage and explorer left open as deliverables.
