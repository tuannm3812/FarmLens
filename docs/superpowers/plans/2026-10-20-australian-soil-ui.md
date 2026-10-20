# Australian soil and interface update

User selected a polish of the existing Streamlit app using the Sites local workflow.

1. Verify CSIRO SLGA point queries, property units and depth intervals. Use key-free ArcGIS identify (the separate TERN raster API now documents a key requirement).
2. Add fixture-tested Australian soil client: four properties, three depth intervals, modelled values and 5th/95th bounds; one retry, cached fallback, no fabricated soil values. Keep precise soil coordinates so kilometre-wide cache buckets do not alias 90 m cells.
3. Connect scoring and scripts. Abstain when pH is unavailable. Show depth profiles, actual query coordinates, retrieval dates and source links; do not represent model output as a field test or uncertainty as a success probability.
4. Refine the existing interface with a quiet field-notebook palette, clear hierarchy, monochrome outline icons, compact cards and visible evidence. Preserve Streamlit, map interaction and explanation behavior.
5. Fetch the three presets, run offline regression tests, inspect the live browser at desktop and narrow widths, save a screenshot, review changes.

Known limits: SLGA is modelled (~90 m), not current soil sampling; map service aliases do not expose a dependable release date, so preserve exact service/layer identifiers and retrieval time without claiming a product vintage. Weighted depth bounds are an indicative envelope, not a joint 90% interval. Crop profiles and weights still require agronomic validation.
