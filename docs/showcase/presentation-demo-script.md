# FarmLens | Codex Builder Day

Landscape showcase; three minutes total, including demo actions. A3 is the chosen print default, not an event requirement. This is a spoken pitch and demo run sheet, not a slide deck.

## Three-minute presentation

Use the bold phrases as memory cues, not words you have to recite exactly. Each spoken sentence starts on its own line. Pause briefly for the clicks; timings are rehearsal targets. If a request takes more than five seconds, use the recorded screenshot.

**Remember the flow:** Question → Land snapshot → Weather → Crop options → Water → Next steps.

### 0:00-0:20 | The question

**On screen:** Start on the prepared Dubbo Land overview.

Hi everyone, this is **FarmLens**.  
It starts with a question: **what could I grow on this land?**  
There's a lot to consider, from the soil to the weather and available water.  
FarmLens brings those pieces together, so you've got a clearer place to start.

### 0:20-0:55 | Start with the land

**On screen:** Point to the selected location, then Land snapshot; stay on Dubbo.

**Let me show you around.**  
I've picked **Dubbo**, but you can search or choose a spot on the NSW map.  
When a place name is available, the app helps you recognise the area.  
First, this **land snapshot** shows mapped land cover and estimated soil conditions.  
The cover label comes from satellite mapping for **2025**.  
It's a first look at the location, rather than a farm inspection.

### 0:55-1:20 | Put the weather in context

**On screen:** Point to Seven-day weather; briefly expand Seasonal climate, then scroll down.

**Next, let's look at the weather.**  
Here's the **seven-day forecast**, with daily rain and temperatures.  
And here are the **seasonal patterns**, showing longer-term rainfall and temperature.  
That helps separate what's coming this week from what's typical across the year.  
You can check the dates and sources as you go.

### 1:20-1:50 | Explore the crop options

**On screen:** Scroll to Explore crop options; open one candidate, then close it.

**With that picture in mind, we can explore crop options.**  
Choose whether you're exploring the land or thinking about a planting month.  
Then open a crop to see **why it appears**, and what needs checking.  
The score helps compare options, but it doesn't guarantee success.  
The aim is to give you better questions to take to a local expert.

### 1:50-2:30 | Ask about water

**On screen:** Open the prepared Wheat / May water result; point to assumptions and the poster chart.

**One of those questions is: would there be enough water?**  
This separate tool compares **ten past growing seasons** using assumptions you can change.  
Here, the same wheat setup shows a bigger water gap at **Broken Hill** than Dubbo.  
You can explore how soil-water storage and crop timing affect the result.  
The starting values are examples, rather than measurements from the selected farm.  
It's historical context alongside the crop shortlist, and doesn't change its rankings.

### 2:30-3:00 | Close with the purpose

**On screen:** Return to Land overview or the poster; keep the disclaimer visible.

**So, what's next for FarmLens?**  
The prototype now connects the land snapshot, weather, crop choices and water questions.  
There are **automated checks**, and the next step is feedback from agronomists.  
I'd also like to compare the results with real farm measurements.  
The goal is a **clearer starting point**, with reasons you can follow.  
**Indicative only.**  
**Check with a local agronomist.**

## 60-second version

**0:00-0:12:** introduce yourself and the six-hour build. **0:12-0:30:** explain the intended users and their problem. **0:30-0:52:** show the prepared Dubbo overview, scroll to crop options and open one crop. **0:52-1:00:** close and thank the audience. Keep water as a verbal mention; use screenshots if clicks are slow.

Hi everyone, I'm **Mike**, a **Master of Data Science student at UTS**.  
For today's **six-hour build**, I'm creating **FarmLens**.  
It's for **NSW farmers and landowners** exploring what crops could suit their land.  
Weather, soil and crop information is scattered, making it hard to know where to start.  
FarmLens brings it together and explains **why each crop appears**.  
**Let me show you.**  
Here's **Dubbo**, with a land snapshot and the weather outlook.  
Scrolling down, I can explore crop options and open one to see **the reasons**.  
There's also a water tool to explore different assumptions.  
The goal is a **clearer starting point** for local advice.  
**Indicative only.**  
**Check with a local agronomist.**  
**Thank you!**

## Demo preparation and recovery

- Use the custom interface at http://127.0.0.1:8503/. The retained Streamlit alternative is on 8502; the script uses custom-UI labels.
- Before presenting, choose Dubbo, enable **Cached data only** in **Scenario help & data options**, choose **Explore my land**, **Rainfed**, **All crops**, and drainage **Unknown**. Existing map assets/tiles may still need internet on a cold load.
- Start at **Land overview** with **Land snapshot** and **Seven-day weather** visible. Briefly expand **Seasonal climate**, then scroll to **Explore crop options**.
- Open **Assess seasonal water · 3-crop pilot** or **Water feasibility**. Select **Wheat**, **May** and **Reset illustrative assumptions**. Confirm 100 mm buffer, 50 mm starting water, 80% infiltration, 80% efficiency and stages 20 / 30 / 60 / 40 days. Click **Calculate water scenario**, then collapse the panel until its cue.
- Keep the prepared result at Dubbo. Show Broken Hill from the poster chart, rather than spending the three-minute slot fetching another location. Location changes reset water assumptions.
- The recorded Dubbo example is 255 mm median demand, 60 mm additional net water and 0.75 ML/ha estimated gross irrigation. The 0.00-2.65 ML/ha interval is the historical 10th-90th percentile sample range, not a forecast interval. It is an estimate to cover the modelled gap, not supplied irrigation in the rainfed case.
- If time slips, skip opening the profile and point to the screenshot. If data are unavailable or differ, state the source status and use the labelled recorded example; do not present saved values as a new live result.
- Do not wait on optional OpenAI or FIRMS credentials. Rule-based explanations are available; credentialed live calls are not part of this demo.

## Screenshot fallback

Use the existing files without editing them:

1. `../screenshots/land-overview.png` - current recorded land snapshot, seven-day weather and seasonal-climate entry.
2. `../screenshots/pin-place-name.png` - clicked map point with a nearby locality label; use as an optional backup.
3. `../screenshots/harvest-workspace.png` - earlier crop shortlist layout; use for the crop cards only.
4. `../screenshots/crop-profile-assets.png` - recorded profile; note that the photo is an example crop, not the selected site.
5. `../screenshots/water-feasibility.png` - recorded Dubbo wheat / May water result.

These are recorded views; the older profile and water screenshots predate the Land overview layout. Place-name lookup is now implemented and fixture-tested. It gives nearby locality context, not a confirmed farm address, and leaves the selected analysis coordinates unchanged. Keep Dubbo selected during the timed demo; use the saved pin-name image if you want to show this feature without loading a new point.

## Short answers for questions

- **Is the land snapshot current farm health?** No. Land cover is a 2025 satellite classification at a 30 m pixel; soil is modelled. Land cover is context and does not affect crop scores.
- **Does the forecast choose the crops?** No. The seven-day outlook is context; rankings use historical climate. Seasonal charts show historical monthly averages.
- **Does the place label identify my property?** No. It is a nearby locality or area label; the selected point remains unchanged.
- **Is this trained machine learning?** No. Recommendations use explicit environmental ranges, weights and eligibility checks. Optional generated wording does not choose the crop ranking.
- **What does the score mean?** A provisional screening index, not a probability, yield forecast or profit estimate. Missing factors are handled explicitly.
- **Is the soil measured on this farm?** No. SLGA is a modelled grid. Local soil testing and agronomic interpretation are still needed.
- **Why do wheat and barley match?** Their water profiles intentionally share generic coefficients and stage lengths; this pilot does not distinguish cultivars.
- **Does the water result change the shortlist?** No. The pilot is separate, and its three crops remain available even if absent from the shortlist.
- **What was validated?** Recorded software tests and source fetches. Neither calibrated crop accuracy nor farm irrigation prescriptions have been established.

See `sources-and-notes.md` for the evidence ledger, photo/map credits and production notes.

Indicative only. Check with a local agronomist.
