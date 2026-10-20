# FarmLens coding standards

Adopt the app/product shape from the personal master at
`~/Documents/GitHub/coding-standards/coding_standards.md`. These project rules
also apply when that local reference is unavailable.

## Structure and deliberate overrides

Keep the existing small Python package, custom HTML/CSS/JavaScript app, tests,
curated data and scripts. FarmLens is an application, so notebook-first,
Kaggle submission and modelling-workflow conventions do not apply.
Retain current research/plan filenames; do not rename historical evidence.
Keep the harvest-yellow, green and cream palette rather than adopting Viridis.
Curated crop requirements, small source fixtures, licensed visual assets and
the NSW boundary are intentional distributable data. Runtime API caches are not.

## Code and verification

Use four-space Python indentation, explicit imports, small named functions,
type hints on new reusable interfaces, and docstrings explaining meaningful
contracts. Comments explain decisions and limitations. Avoid unrelated
formatting rewrites of existing modules during feature work.

JavaScript modules keep calculation/presentation helpers testable with
node:test. Escape external text; never inject assistant questions as HTML.
CSS reuses the existing design tokens, keyboard focus and reduced-motion rules.

Test calculations and failure boundaries with fixtures and no live network.
Unknown, zero, stale and unavailable are different states. Every point-specific
async view invalidates previous requests/results when its context changes.
`python scripts/check.py` runs compilation, Python tests, JS syntax and JS tests.
GitHub Actions runs that same command; a local pass is not a hosted CI result.

## Evidence and claims

Keep source links, reference periods, units, grid/depth resolution and meaningful
limits accessible. Scores are screening indices. Soil is modelled. Imagery
dates describe source blocks, not live conditions. Water and budget tools are
explicit scenarios. No general field-validation, yield or profit claims.

## Privacy and repository hygiene

Do not commit `.env`, credentials, API caches or temporary rendering outputs.
The local report guide sends no typed question. The optional OpenAI wording
feature retains its numeric-only contract. Use one coherent Conventional Commit
when committing is requested; inspect intended paths first.
Record actual verification commands and results with dates, never assumed passes.
