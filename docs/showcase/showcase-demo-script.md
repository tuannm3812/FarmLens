# FarmLens — local showcase script

Prepared 20 October 2026. Use the custom app at http://127.0.0.1:8503/.
Start on Home; have Dubbo cached. This version supersedes the earlier demo script
for today's finished interface. Previous files are retained as historical work.

## Three-minute walkthrough

### 0:00–0:25 · The question

**On screen:** Home, then Explore your land.

Meet FarmLens, a friendly farming companion built around one question:
what could I grow on this land?
Climate, soil and crop information often live in different places.
FarmLens brings them into one view, with reasons you can inspect.
Let me show you the local prototype.

### 0:25–0:55 · Start with the land

**On screen:** Dubbo → Land snapshot → View land, then close the image.

I’ll start with Dubbo. You can also choose a point on the NSW map.
The snapshot combines modelled Australian soil with mapped land cover.
The image gives geographical context around the pin.
Its survey date is visible: this Dubbo block dates to 2009, so it is not a live view.
The preset is a town-centre demo point, not a verified farm.

### 0:55–1:15 · Weather in context

**On screen:** Seven-day weather; point to the collapsed Seasonal climate summary.

Here is the seven-day weather outlook.
The crop screen uses longer-term climate patterns, kept separately.
The app shows dates and source status, including when data are cached.
That distinction matters: a forecast, a historical average and a soil model
are different kinds of evidence.

### 1:15–1:50 · Crop options and their reasons

**On screen:** Scroll to Crop options; open Canola, inspect factors, close.

Now we can explore crop candidates.
Each score uses explicit ranges and weights for climate and soil factors.
NSW guidance adds checks and constraints, while the weakest factor is visible.
Opening a crop shows the detail, including what has not been assessed.
A high score is a stronger environmental screen, not a probability of success.
The next step is still local advice and field measurements.

### 1:50–2:25 · Meet Finn

**On screen:** Return to the report header → Ask FarmLens → Why this crop?

Finn makes that report easier to discuss.
I can ask why a crop appears, what to watch, or how to explore water and budgets.
For this demo, Finn uses supported questions and the existing report numbers.
Typed questions stay in the browser.
Optional model-written crop explanations are separate and receive only the
approved numeric inputs.

### 2:25–3:00 · Trade-offs and next step

**On screen:** What about water? → Open water planner; briefly indicate Crop budget.

The water pilot explores ten historical seasons under assumptions you can change.
The budget tool explores gross margin from entered yield, price and costs.
Both sit alongside the shortlist; neither predicts the farm’s future return.
What I want to test next is whether this makes a useful first conversation
with a farmer or agronomist.
Indicative only. Check with a local agronomist.

## 60-second backup

Meet FarmLens, a local prototype for exploring what could grow on land in NSW.
Drop a pin to bring climate, modelled Australian soil and crop requirements
into one report.
The land snapshot includes dated imagery, while the crop shortlist explains
its scores and limitations.
Finn is a friendly guide to that report, answering supported questions locally.
Separate water and budget tools let you explore assumptions.
The purpose is a clearer starting point for local advice, not a yield or profit forecast.
I’m looking for feedback on what would make it useful in practice.
Indicative only. Check with a local agronomist.

## Before recording or presenting

1. Run `.venv/bin/python -m farmlens.web`; open Home at port 8503.
2. Select Dubbo. Use **Cached data only** under **About these inputs & data**
   for the prepared report. Map tiles and NSW imagery can still need internet.
3. Check the displayed forecast dates before describing the outlook as current.
4. Confirm the land image loads and shows its survey date. An unavailable image
   is acceptable; use the recorded screenshot rather than inventing context.
5. Open Finn once, then close it. Test the optional explanation only if needed;
   rule-based wording works without OpenAI credentials.
6. Keep the final screenshots available. If a request takes more than five
   seconds, switch to one and call it a recorded example.

## Keep these distinctions clear

- Scores: provisional environmental indices, not validated planting advice.
- Soil: modelled 0–30 cm values, not a soil test at the farm.
- Imagery: dated survey-block context, not live conditions or a property boundary.
- Water: historical scenarios with illustrative storage and crop-timing inputs.
- Budget: gross margin excludes overheads, finance and tax; archived 2012 examples
  are not current prices.
- Finn: bounded local report guide, not an agronomist or general chat model.
- Verification: 305 Python and 43 JavaScript tests passed on 20 October 2026.
  Software checks do not establish agronomic accuracy.

## Recorded fallback images

- `../screenshots/showcase-home.png`
- `../screenshots/showcase-explorer.png`
- `../screenshots/showcase-crops.png`
- `../screenshots/showcase-finn.png`
- `../screenshots/showcase-mobile-guide.png`

See `showcase-release-notes.md` for source credits, verification and remaining work.
