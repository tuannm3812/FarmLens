# Step 2 checkpoint — 2026-10-20

These are **provisional environmental screening candidates**, not validated planting recommendations. Scores are an uncalibrated index, not yield or probability. This report uses cache-only mode; no API calls or LLM calls were made to generate it.

**Evidence:** real climate is used where a valid local cache exists; soil can be offline regional estimates. Every scenario below shows its own evidence status. Fire is unassessed and its weight excluded. A score of 100 means all assessed proxy factors were in their optimal ranges, not that all farm constraints were checked.

May and October are month scenarios using historical climate, not forecasts for a specified year. Annual rainfall is still the rainfall score input in both modes. Irrigation is unquantified and gives no score bonus.

## Rainfed scenarios

| Location | Mode / month | Highest-scoring candidates | Result | Evidence |
| --- | --- | --- | --- | --- |
| Coffs Harbour | Explore my land | Improved pasture (ryegrass proxy) 100.0; Macadamia 100.0; Citrus (sweet orange proxy) 99.9 | Proxy score passes demo threshold | provisional — offline inputs |
| Coffs Harbour | Plan next season / 05 | Lentil 90.8; Chickpea 74.2; Oats 72.4 | Proxy score passes demo threshold | provisional — offline inputs |
| Coffs Harbour | Plan next season / 10 | Cotton 65.0; Sorghum 20.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Explore my land | Barley 100.0; Canola 100.0; Chickpea 100.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Plan next season / 05 | Barley 95.3; Canola 93.9; Lentil 91.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Plan next season / 10 | Sorghum 97.3; Cotton 84.2 | Proxy score passes demo threshold | provisional — offline inputs |
| Broken Hill | Explore my land | Barley 20.0; Canola 20.0; Chickpea 20.0 | No strong match | provisional — offline inputs |
| Broken Hill | Plan next season / 05 | Barley 20.0; Canola 20.0; Chickpea 20.0 | No strong match | provisional — offline inputs |
| Broken Hill | Plan next season / 10 | Cotton 20.0; Sorghum 20.0 | No strong match | provisional — offline inputs |

## Irrigated scenarios

| Location | Mode / month | Highest-scoring candidates | Result | Evidence |
| --- | --- | --- | --- | --- |
| Coffs Harbour | Explore my land | Improved pasture (ryegrass proxy) 100.0; Macadamia 100.0; Citrus (sweet orange proxy) 99.9 | Proxy score passes demo threshold | provisional — offline inputs |
| Coffs Harbour | Plan next season / 05 | Lentil 90.8; Chickpea 74.2; Oats 72.4 | Proxy score passes demo threshold | provisional — offline inputs |
| Coffs Harbour | Plan next season / 10 | Rice 94.3; Cotton 65.0; Sorghum 20.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Explore my land | Barley 100.0; Canola 100.0; Chickpea 100.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Plan next season / 05 | Barley 95.3; Canola 93.9; Lentil 91.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Dubbo | Plan next season / 10 | Sorghum 97.3; Cotton 84.2; Rice 20.0 | Proxy score passes demo threshold | provisional — offline inputs |
| Broken Hill | Explore my land | Barley 20.0; Canola 20.0; Chickpea 20.0 | No strong match | provisional — offline inputs |
| Broken Hill | Plan next season / 05 | Barley 20.0; Canola 20.0; Chickpea 20.0 | No strong match | provisional — offline inputs |
| Broken Hill | Plan next season / 10 | Cotton 20.0; Rice 20.0; Sorghum 20.0 | No strong match | provisional — offline inputs |

## Rainfed detail

### Coffs Harbour — Explore

- **Improved pasture (ryegrass proxy) — 100.0/100** (pasture). Weakest factor: none among assessed proxies (all tied at 100). Sub-scores: temperature 100.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
- **Macadamia — 100.0/100** (perennial). Weakest factor: none among assessed proxies (all tied at 100). Sub-scores: temperature 100.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
- **Citrus (sweet orange proxy) — 99.9/100** (perennial). Weakest factor: temperature. Sub-scores: temperature 99.5, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.

### Coffs Harbour — Season month 5

- **Lentil — 90.8/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 72.4, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 16.4°C mean; 312.2 mm rain; 0.0 days/year below 0°C; 0.0 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Chickpea — 74.2/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 48.2, ph 61.5, frost 100.0, fire unassessed.
  Historical growing-period context: 16.4°C mean; 312.2 mm rain; 0.0 days/year below 0°C; 0.0 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Oats — 72.4/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 17.1, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 17.0°C mean; 433.5 mm rain; 0.0 days/year below 0°C; 0.0 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

### Coffs Harbour — Season month 10

- **Cotton — 65.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 28.5, ph 50.0, frost 100.0, fire unassessed.
  Historical growing-period context: 22.9°C mean; 1009.5 mm rain; 0.0 days/year below 0°C; 1.8 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Sorghum — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 22.9°C mean; 727.4 mm rain; 0.0 days/year below 0°C; 1.8 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

### Dubbo — Explore

- **Barley — 100.0/100** (annual). Weakest factor: none among assessed proxies (all tied at 100). Sub-scores: temperature 100.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
- **Canola — 100.0/100** (annual). Weakest factor: none among assessed proxies (all tied at 100). Sub-scores: temperature 100.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
- **Chickpea — 100.0/100** (annual). Weakest factor: none among assessed proxies (all tied at 100). Sub-scores: temperature 100.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.

### Dubbo — Season month 5

- **Barley — 95.3/100** (annual). Weakest factor: temperature. Sub-scores: temperature 83.1, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 12.8°C mean; 272.4 mm rain; 8.9 days/year below 0°C; 0.2 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Canola — 93.9/100** (annual). Weakest factor: temperature. Sub-scores: temperature 78.0, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 12.8°C mean; 272.4 mm rain; 8.9 days/year below 0°C; 0.2 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Lentil — 91.0/100** (annual). Weakest factor: temperature. Sub-scores: temperature 67.6, rainfall 100.0, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 11.8°C mean; 215.4 mm rain; 8.9 days/year below 0°C; 0.0 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

### Dubbo — Season month 10

- **Sorghum — 97.3/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 92.0, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 23.0°C mean; 280.8 mm rain; 0.0 days/year below 0°C; 27.6 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Cotton — 84.2/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 52.7, ph 100.0, frost 100.0, fire unassessed.
  Historical growing-period context: 23.0°C mean; 350.3 mm rain; 0.0 days/year below 0°C; 30.5 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

### Broken Hill — Explore

- **Barley — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
- **Canola — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
- **Chickpea — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.

### Broken Hill — Season month 5

- **Barley — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 85.2, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 13.1°C mean; 94.6 mm rain; 4.0 days/year below 0°C; 0.8 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Canola — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 80.8, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 13.1°C mean; 94.6 mm rain; 4.0 days/year below 0°C; 0.8 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Chickpea — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 62.7, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 12.0°C mean; 73.3 mm rain; 4.0 days/year below 0°C; 0.1 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

### Broken Hill — Season month 10

- **Cotton — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 23.4°C mean; 84.2 mm rain; 0.0 days/year below 0°C; 44.0 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.
- **Sorghum — 20.0/100** (annual). Weakest factor: rainfall. Sub-scores: temperature 100.0, rainfall 0.0, ph 100.0, frost 100.0, fire unassessed. Zero-factor cap applied.
  Historical growing-period context: 23.4°C mean; 73.4 mm rain; 0.0 days/year below 0°C; 38.5 days/year at or above 35°C. Monthly mean minima are a proxy and can conceal individual frosts.

## Interpretation

The coastal seasonal shortlist needs special scrutiny: broad global crop ranges alone can rank lentil highly despite unassessed drainage, disease and regional production constraints. This is an unresolved agronomic-validation gap, not evidence that lentil should be planted near Coffs Harbour. Do not tune weights merely to obtain a more familiar-looking demonstration.

No strong match means all eligible candidates failed the demo's score threshold or hit an absolute limit. Where several crops tie at the 20-point cap, their alphabetical order has no agronomic meaning. The JSON companion contains every sub-score, excluded crop, source status and scenario warning.

Indicative only. Check with a local agronomist.
