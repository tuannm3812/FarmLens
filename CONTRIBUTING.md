# Contributing

FarmLens is a local NSW crop-screening prototype. Useful contributions include
reproducible bug reports, accessibility improvements and source-backed corrections.
Agronomic review is especially valuable; software tests do not establish crop accuracy.

## Development

Follow the [README setup](README.md#run-locally) and use Python 3.11 plus Node.js 22
for checks. From the repository root:

```sh
python -m pip install -e '.[dev]'
python scripts/check.py
```

Tests use fixtures and block live HTTP calls. Use a targeted test while working,
then run the complete check before opening a pull request. Include what changed,
why it matters and the validation performed.

## Changes that need evidence

- Cite the source and units when changing crop requirements or guidance.
- Keep pH in water separate from pH measured in calcium chloride.
- Preserve distinctions between zero, missing, stale, modelled and observed data.
- Keep crop scores, water scenarios, budgets and imagery separate.
- Invalidate old results when the selected location changes.
- Keep typed Finn questions local; optional model explanations use the numeric allowlist.
- Retain licences and attribution when adding visual assets.

Do not commit API keys, `.env` files, downloaded caches or personal farm data.
Public issues should use synthetic examples or the supplied town-centre demo points.
The local server is not a production deployment target.

Project conventions: [AGENTS.md](AGENTS.md) and
[coding standards](docs/0_coding_standards.md).
