# FarmLens

FarmLens is a local NSW crop-screening showcase, with a Python engine and a
custom web interface. Its scores are provisional indices, not yield forecasts.

## Standards

Project rules are in `docs/0_coding_standards.md`.
They are self-contained for contributors.

## Working agreement

- Preserve the existing `farmlens/` + `web/` structure and optional Streamlit UI.
- Keep scoring, water scenarios, budgets and visual context separate.
- Never substitute invented soil, satellite observations, dates or prices.
- Clear location-dependent results as soon as selection changes.
- Guide questions stay in the browser. Optional model explanations send only
  the numeric allowlist in `farmlens/explain.py`.
- Use original SVG assets and licensed local photos/fonts with attribution.
- Run `python scripts/check.py` for a release; use targeted checks while editing.
- No public hosting, social posting or credential-dependent claims by default.

## Documentation

- The README describes the current scope and public roadmap.
- `docs/technical-reference.md` explains methods and limitations;
  `docs/research/` retains the detailed source reviews.
- Keep personal scripts, draft posts, plans and housekeeping in ignored
  `docs/internal/`. Local diagnostic outputs use ignored `docs/checkpoints/`.
- Do not link public documents to ignored files or republish local notes.
- Keep the public showcase snapshot, poster and their attribution together.
