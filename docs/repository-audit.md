# Repository release audit — 20 October 2026

Scope: publish the working local showcase as `tuannm3812/FarmLens`, with MIT for
original code, after a source and release-hygiene audit. This is not public app
deployment or a claim of agronomic calibration.

## Runtime findings and fixes

| Finding | Fix | Regression evidence |
| --- | --- | --- |
| Lord Howe Island passed NSW boundary validation but failed a mainland-only imagery bound, interrupting the report. | Include the island extent and contain an invalid imagery point within the optional image view. | Two Node cases failed before the fix and pass afterward; offline API analysis accepts the island and keeps absent soil unknown. |
| Failed-refresh and cache-only warning wording produced different explanation fingerprints for identical stale evidence. | Fingerprint semantic evidence state and timestamps, excluding retrieval prose. | A real fixture-backed climate cache with simulated timeouts reproduced the mismatch. The new case passes; fresh-to-stale rejection still passes. |
| The land snapshot accepted soil fractions above 100%, unlike scoring. | Apply the same non-negative, total-at-most-100 boundary. | New Node case failed before the fix, then passed for excess, negative and valid boundary inputs. |
| Zero per-hectare costs and zero per-tonne contribution were labelled as an unreachable break-even yield. | Explicitly report “Any yield (zero margin)”. | New Python calculation and Node rendering cases failed before the change, then passed. |

An independent read-only reviewer found no Critical issue within the local
loopback scope and independently passed 181 targeted Python / 29 Node cases.
Both Important and both Minor findings from that review are addressed above.

## Repository polish

- A concise README now provides the overview, screenshot, setup, sources,
  limitations, development command and licensing.
- Detailed historical implementation notes moved to `technical-reference.md`;
  all relative links in the entry-point documents were checked.
- Added MIT, third-party notice, contribution notes and a documentation index.
- Broadened exclusions for environment files, nested runtime caches, build
  outputs, bytecode and local tooling scratch files.
- Removed the remaining machine-specific Playwright import from showcase tooling.
- All 15 crop images match their recorded SHA-256 hashes and have creator,
  source and licence fields.

## Local verification

`python scripts/check.py` passed **307 pytest cases and 47 Node cases**, plus
Python compilation and JavaScript syntax checks. `pip check` found no broken
requirements. Credential-pattern scanning found no matches in candidate text
files. `.env`, `.env.local`, nested cache files, `.venv` and bytecode are excluded.

The updated local server was restarted, and the browser completed the
rule-based crop explanation flow. Earlier desktop/mobile screenshots and PDF
materials remain recorded showcase evidence; their earlier test counts are not
the current release total.

A clean copy containing only staged paths also passed all 307 Python / 47 Node
cases. Editable-install metadata was generated with no network and no dependency
changes. The copy contained neither runtime caches nor environment files.

## Remaining limits

- No live credentialed OpenAI/FIRMS verification or agronomic calibration.
- No public web deployment. The current server is deliberately loopback-only.
- Image-provider outages were not forced during browser QA; client failure
  boundaries and optional-image exception containment have automated coverage.
- The previously recorded minor multi-block imagery-date presentation follow-up
  remains in `showcase/showcase-release-notes.md`.

## Publication

The public repository is [tuannm3812/FarmLens](https://github.com/tuannm3812/FarmLens).
The initial code commit is `74f7e00`. GitHub recognized the MIT licence, and the
[first CI run](https://github.com/tuannm3812/FarmLens/actions/runs/39388715220)
completed successfully with a fresh Ubuntu installation, Python 3.11 and Node 22.
Subsequent release-documentation changes do not alter the tested application.
