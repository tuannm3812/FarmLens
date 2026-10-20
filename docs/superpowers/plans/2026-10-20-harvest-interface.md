# Harvest interface implementation plan

> Execution: native implementation using superpowers:executing-plans; one independent final review.

**Goal:** Apply the approved Harvest palette, modern fonts and report-first layout, with an optional crop comparison.
**Architecture:** Keep the current Python API and seven-factor scores. Rearrange custom HTML/CSS, preserve all provenance and guidance, use a native dialog for one crop's details and a small pure JS comparison module. Retained Streamlit receives the same colour/font treatment.
**Stack:** Existing HTML/CSS/JS, Python, Streamlit; no new runtime framework.
**Spec:** User-approved block review and Harvest preview in this conversation. Font choice: Manrope headings, Inter body/numbers, local files and system fallbacks.

## Constraints and rulings
- All work stays in the user's existing checkout: repository has no HEAD and all current app work is untracked, so a worktree cannot preserve this working app. No unsolicited initial commit.
- User explicitly requested applying all changes now; no further design or execution approval is required.
- Palette: yellow #E7B83C, ink #252A26, ivory #F7F4EB, green #355B48, blue #316B83, caution #A5442D. Yellow controls use dark text.
- CSS/layout checked visually rather than tests that mirror style declarations. Meaningful data-comparison tests precede implementation.
- Do not alter crop scores, data source rules or numbers-only explanation payload.

## Tasks
- [x] 1. Fetch and bundle licensed fonts; apply colour/type tokens to custom and retained Streamlit UIs. Verify local font responses and computed body/heading styles.
- [x] 2. Rearrange header/map/report (roughly 40/60), collapsed condition editor, five-value summary, compact shortlist, crop detail dialog, outlook below results, source panel and integrated explanations. Preserve search/race/location/reset handling, errors, accessibility and privacy captions. Verify browser flows at desktop and mobile.
- [x] 3. Add comparison.js with pure buildComparison model and SVG renderer. Tests must cover missing factors as null (no zero substitution), actual zero scores, selected series and incomplete paths. Add optional accessible comparison with exact-value table. Verify offline pytest and Node suites, independent review, screenshot and README.

## Review focus
- Location/scenario changes while detail dialog or explanation is open must not display old crop data.
- Missing soil/fire factors cannot become plotted zeroes or a closed misleading shape.
- Keyboard dialog opening, closing and focus return; mobile overflow and map collapse.
- Source disclaimers and actionable errors remain reachable when controls collapse.
- Font delivery works offline and adds no arbitrary static-file access.

## Verification ledger
- Baseline: 181 offline Python tests passed.
- Comparison: missing module failed before implementation; 4 Node tests now pass for missing/zero/selection/invalid score cases.
- Local assets: 3 routes first failed with 404, then passed after explicit allowlisting; arbitrary paths remain 404. Full Python suite: 184 passed.
- Review: one P2 found (Explain errors hidden on Data & sources). Reproduced with local server stopped: error text present but invisible. Moved shared status above tabs and added actionable network message.
- Review ruling: factor table labelled exact while rounding is misleading; use “Factor scores (rounded)” and one decimal. Mobile selection should not leave focus in a hidden map; focus report after auto-collapse. Both are small correctness/accessibility fixes within the requested refinement.
- Browser: local fonts declared as Inter body/Manrope headings; drawer Escape returns focus to initiating crop button; source checks visible; missing fire remains unassessed; selective radar series and rule-based explanations verified. Final mobile check: map collapses, focus reaches report, radar/table fit without horizontal overflow. Controlled server failure after the fix shows an actionable visible error on Data & sources.

- Final review complete: no critical issues; global Explain status fixed and verified before/after in browser. Table wording and mobile focus refinements applied. Both test suites remain green. Screenshot captured for handoff.
