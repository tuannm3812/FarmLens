# FarmLens current completion checklist

Target: polished local showcase, 20 October 2026. This is the current checklist;
dated implementation plans and test counts remain historical evidence.

Repository publication was subsequently authorized: public `tuannm3812/FarmLens`,
MIT for original code. The [release audit](repository-audit.md) records four
correctness fixes and the current local total of 307 Python / 47 Node cases.

## Already built

- Climate, Australian modelled soil, sourced crop profiles, transparent scores
  and source-linked NSW guidance checks.
- Custom map app, address/pin locality, Home / Explore / How it works navigation.
- Crop photos/icons, weather, historical climate and DEA land-cover context.
- Historical water pilot, budget scenarios and vegetation cover observations.
- Numeric-only optional OpenAI explanations and rule fallback.
- Earlier poster and presentation script.

## Finished for the local showcase

- [x] Relevant coding standards, reusable check command and CI configuration.
- [x] Friendly logo, wordmark, favicon and separate Finn avatar.
- [x] Selected-point NSW imagery and concise land snapshot.
- [x] Ask FarmLens with supported local questions and preserved optional explanation.
- [x] Desktop/mobile checks, fixture-based failure verification and fresh code review.
- [x] Updated poster, demo script, share image and LinkedIn draft.

Evidence and precise verification limits:
[`showcase-release-notes.md`](showcase/showcase-release-notes.md).
Final local app checks: 305 Python / 43 Node cases. The local server remains on
port 8503. PDFs and share image were rendered and visually inspected.

## Deliberately outside today's completion

- Public hosting, voice and user accounts.
- Agronomist-labelled validation/calibration and additional seasonal/cultivar data.
- Live market prices or farm-specific yield/profit prediction.
- Credential-based OpenAI and FIRMS live checks unless keys are supplied.
- Minor imagery follow-up: list individual dates when multiple survey blocks
  intersect a point; the current view explicitly says “Multiple survey dates”.

The original plan's unchecked UI/explanation/client tasks have subsequent
implementation evidence. Its original pauses and progress notes are historical,
not today's backlog. FIRMS code/fixtures exist; this is not a claim that
credentialed historical coverage has been verified in this environment.
