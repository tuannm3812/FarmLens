# FarmLens

FarmLens is a local NSW crop-screening showcase, with a Python engine and a
custom web interface. Its scores are provisional indices, not yield forecasts.

## Standards

Use `~/Documents/GitHub/coding-standards/coding_standards.md` when available.
Project rules and deliberate overrides are in `docs/0_coding_standards.md`.
That file is self-contained for contributors without the personal master.

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

## Evidence and current state

- `docs/4_next_steps.md` is the current completion checklist.
- `docs/3_decisions.md` records meaningful decisions.
- `docs/research/` and `docs/checkpoints/` hold source and validation evidence.
- Historical plans under `docs/superpowers/plans/` retain their original record.
- The target agreed on 20 October 2026 is a polished local showcase.
