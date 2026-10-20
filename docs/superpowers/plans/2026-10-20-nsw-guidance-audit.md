# NSW guidance and frontend audit implementation plan

> Execution: inline backend work with an independent frontend implementer and final fresh-context review, using the existing authorized local app.

**Goal:** Check the crop screen against NSW agronomy, enforce compatible constraints, expose evidence gaps, and fix both frontend audits without claiming empirical validation.

**Architecture:** Keep seven transparent proxy scores. Add a versioned NSW guidance catalogue and independent assessment in `farmlens/agronomy.py`. Compatible explicit conflicts remove candidates from the shortlist, with full reasons preserved. Unknowns never become passed checks or artificial numeric penalties. Add optional user-reported drainage, reset on point changes. PHW is not converted to pHCa. Retain local custom UI and Streamlit.

- [x] Source review: all 15 crops, publication/version/page, compatible data versus missing observations. Record validation limits; no invented regional polygons, pH conversions or tuned weights.
- [x] Add failing tests for rainfed macadamia <1200 mm, lentil <=300 mm, fallback/stale climate non-exclusion, drainage conflicts, missing pHCa, unknown guide coverage, explanation cautions and API validation. Implement catalogue, assessment, scoring integration and same-origin API contract.
- [x] Frontend fixes: per-crop labels and notes, guidance/source details and exclusions; drainage; clear seasonal/pH wording; state/search races; actionable errors; contrast, keyboard focus and compact shortlist. Keep original user data untouched.
- [x] Full offline tests, frontend syntax, review and desktop/mobile/browser checks; save audit/checkpoint/preview with remaining validation needs.

Ruling: this is an evidence-based refinement of the approved existing architecture, not a redesign needing another approval. No public deployment or new external messaging. No experimental ranking accuracy claim: a guidance consistency check cannot replace blinded agronomist review or held-out NSW trial validation. The numeric model remains an uncalibrated baseline; source-backed eligibility and explicit unknowns improve defensibility.
