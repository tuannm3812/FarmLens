# FarmLens architecture

`python -m farmlens.web` runs the loopback-only Python server. Fixed routes serve
Home, Explore and How it works. A shared navigation partial connects them.
The optional `streamlit run app.py` uses the same Python engine.

Selected-point clients retrieve climate, SLGA soil, optional FIRMS history,
Nominatim locality, DEA land cover and vegetation. JSON responses use validated
file caches, bounded timeouts and one retry. Missing evidence is explicit.
NSW imagery dates use the same client contract; the browser loads the bounded
image directly from NSW Spatial Services.

`scoring.py` combines approximate crop requirements and compatible NSW checks.
Water and budget calculations are independent modules; imagery and land cover
are visual context and do not alter scores.

The custom frontend is plain HTML/CSS/JS with Leaflet. Modules own their report
panels and invalidate old context on selection changes. Session storage retains
only a valid point and scenario, with generic labels.

Ask FarmLens answers supported questions locally from the loaded report.
The separate optional model explanation request uses the existing numeric
allowlist, server-side key, bounded timeout and deterministic fallback.

Fixtures, pytest and node:test cover contracts without live requests. Browser
checks verify assembled desktop/mobile flows; they do not prove agronomic accuracy.
