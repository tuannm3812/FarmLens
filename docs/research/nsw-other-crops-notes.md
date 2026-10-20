# NSW guidance audit: summer crops, pasture and horticulture

Research checked 20 October 2026. Scope: sorghum, cotton, rice, lucerne, grapes, olives, citrus and the perennial-ryegrass pasture proxy. Existing `data/crops.csv` and `data/README.md` were read. No scoring thresholds or code were changed in this research task.

## Interpretation and compatibility

FarmLens currently has annual/seasonal historical air-climate summaries, a water-scenario choice, and modelled SLGA 0–30 cm depth-weighted pH **in water**, clay, sand and organic carbon. It does not measure drainage, infiltration, sodicity, salinity, rooting depth, available stored water, irrigation quantity/quality/reliability, soil temperature or cultivar phenology. Clay percentage alone cannot determine drainage. SOC is not a test of nutrient sufficiency. Most guidance below therefore supports explicit missing checks, not extra numerical penalties.

Do not convert CaCl2 pH into water pH with a fixed offset. Do not treat an ideal or amelioration threshold as a lethal limit. Do not silently replace depth-specific topsoil/subsoil tests with the current 0–30 cm mean. Geographic descriptions of production districts do not justify invented coordinate exclusions.

Where a user supplies `poorly_drained`, the strongest crop-specific evidence here supports a **reported drainage conflict requiring resolution** for lucerne and citrus. Olive evidence supports the same, but the strongest explicit waterlogging statement is an ecological WeedWise profile, not a commercial orchard trial. Cotton supports a drainage-management warning. These are not proof of permanent impossibility: engineering, rootstock, varieties and management may mitigate some constraints.

## Sorghum

**Source:** NSW DPI, [Summer cropping options for northern and central NSW 2022](https://www.dpird.nsw.gov.au/__data/assets/pdf_file/0003/1415388/summer-crop-options-2022.pdf), 2022, pp. 2–5, especially p. 2 Table 1 and pp. 4–5 grain sorghum. Full PDF text read.

The guide ties sowing to soil temperature: conventional guidance is 16–18°C, with experimental early sowing at at least 12°C and rising for three days. Measure at sowing depth near 8 am. Timing should avoid frost and extreme heat during sensitive stages, and yield expectations depend on stored moisture and seasonal conditions. Table 1 gives an ideal pHCa value of 5.5, not an absolute exclusion; sampling depth is not specified there. The guide also identifies salinity and sodicity concerns.

**Missing checks:** sowing-depth temperature, stored available water, sowing/cultivar-specific flowering date, salinity/sodicity, field disease and management. No verified source here supports turning annual rain above the existing EcoCrop maximum into a NSW drainage exclusion. No new deterministic exclusion from present inputs is defensible. No explicit poor-drainage prohibition verified for sorghum in this review.

## Cotton

**Sources:** NSW Agriculture, [SOILpak for cotton growers, third edition, Part A](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0007/167497/soilpak-cotton-Part-A.pdf), pp. A2-3–A2-6 (edition date not verified from retrieved Part A; do not use search-engine crawl dates as publication dates); [current departmental SOILpak landing page](https://www.dpird.nsw.gov.au/agriculture/soils/guides/soilpak-series/soilpak). [Irrigated cotton climate vulnerability assessment](https://www.dpird.nsw.gov.au/dpi/climate/climate-vulnerability-assessment/commodity-pages/irrigated-cotton), current webpage, no publication date displayed in extracted body.

SOILpak requires adequate infiltration, internal/surface drainage, rooting conditions and plant-available water capacity. Drainage design reduces waterlogging; flooding is particularly dangerous for seedlings. Its Table A2-1 lists pH 5.5–7.0 measured in **0.01 M CaCl2** for germination and root growth. The pH entries do not individually specify a sampling depth; other rows refer to topsoil 0–0.1 m for establishment and 0–1 m for root conditions. Do not copy those depths onto pH without further verification. These are targets, not absolute limits.

The climate assessment explicitly separates establishment, vegetative, reproductive, early-boll and late-boll phases, and describes a season up to 180 days. It models irrigated cotton; it cannot establish dryland feasibility.

**Missing checks:** planting soil temperature; season duration and phenology; stored soil moisture and water budget; actual drainage, structure, salinity/sodicity and subsoil. Existing inputs do not support a new hard crop exclusion. Report poor drainage as a conflict to resolve, not permanent land unsuitability.

## Rice

**Sources:** NSW DPI, [Rice growing guide 2021, second edition](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0004/1361173/RGG-2021-web-final-26Oct2021.pdf), pp. 1 and 29; [current guide landing page](https://www.dpird.nsw.gov.au/agriculture/broadacre-crops/summer-crops/rice/rice-growing-guide). The current landing page still links the 2021 guide. Relevant passages retrieved through indexed departmental PDF text; full download exceeded browser size limits. [Irrigated rice climate assessment](https://www.dpird.nsw.gov.au/dpi/climate/climate-vulnerability-assessment/broadacre-cropping/irrigated-rice), current webpage, publication date not shown in body.

The guide requires a pre-sowing crop water budget, preferably based on paddock history or evapotranspiration. Low-permeability soil reduces deep drainage and excess water use; soil texture inferred by EM31 and sodicity testing inform land suitability. Cold stress at microspore must be considered. Page 29's pHCa below 5 is a lime-management trigger: flooding temporarily raises pH, so rice yield is rarely directly limited by acidic soil. No sampling depth is specified in that passage.

**Missing checks:** quantitative irrigation supply, paddock permeability/sodicity and approval/suitability assessment, irrigation layout, cultivar dates and microspore cold protection. A user-selected irrigated scenario does not pass these. Keep the established rainfed-rice exclusion as a disclosed NSW demo scope rule. Do not infer rice suitability from topsoil clay alone or reject it for poor drainage in the same way as upland crops. No additional deterministic exclusion from the existing inputs.

## Lucerne

**Sources:** NSW Agriculture, [Lucerne for pasture and fodder, Agfact P2.2.25, third edition](https://www.dpird.nsw.gov.au/__data/assets/pdf_file/0010/164737/p2225pt1.pdf), 2003, pp. 8–9, 16 and 19; [NSW DPIRD Lucerne species page](https://www.dpird.nsw.gov.au/agriculture/pastures-and-rangelands/species-varieties/lucerne), undated body. Full relevant PDF text read.

The Agfact favours deep, well-drained soils and warns that waterlogging can kill or weaken plants, especially in heat, although established plants can survive brief moving-water floods. Its establishment warning is specifically **top 10 cm pH(Ca) below 5.2 together with exchangeable aluminium above 5%**, and it also calls for subsoil acidity assessment. It describes frost tolerance with possible damage to active growth and seedlings. The current species page lists a preferred pHCa range 5.2–7.5 (no depth specified) and annual rainfall minima of 375 mm in southern and 400 mm in northern NSW; the older Agfact instead describes an approximate southern 350 mm isohyet.

**Missing checks:** deep drainage/rooting, CaCl2 tests at stated depth plus subsoil, aluminium, establishment moisture, disease-resistant variety and intended use. Do not implement a PHW threshold or north/south cutoff from this. Known poor drainage is a defensible warning/conflict; current SLGA texture cannot establish it.

## Grapes

**Sources:** NSW DPIRD, [Wine grapes — Chardonnay climate vulnerability assessment](https://www.dpird.nsw.gov.au/dpi/climate/climate-vulnerability-assessment/commodity-pages/wine-grapes-chardonnay), current undated webpage; NSW Government/Local Land Services, [Starting out in horticulture](https://www.nsw.gov.au/regional-and-primary-industries/agriculture/horticulture/starting-out-horticulture), current undated webpage, “Planning for climate and infrastructure.”

The Chardonnay assessment evaluates dormancy, budbreak, bloom, veraison, maturation and post-harvest separately. It treats frost at budbreak/bloom, heat at bloom/veraison, dormant-season rainfall and irrigation demand as different constraints. It represents Chardonnay, not every grape use or cultivar. The general horticulture guide calls for observing frost pockets, flood/waterlogging risk, slope/runoff, shallow soils and wind across a full season.

**Missing checks:** variety/use/rootstock, sensitive-stage frost and heat, site cold-air drainage, soil profile/drainage/salinity, reliable crop water supply and disease risk. No method-and-depth-specific grape pH limit verified in this review. Annual means cannot replace these checks. Do not hard-exclude all grapes solely for an unverified drainage class from this evidence; use a missing check or general site warning. No new deterministic exclusion from existing inputs.

## Olives

**Sources:** NSW DPI, [Olive tree crops](https://www.dpird.nsw.gov.au/stories/olive-tree-crops), 26 October 2021; NSW DPI [WeedWise — Feral olive (Olea europaea subsp. europaea)](https://weeds.dpi.nsw.gov.au/Weed/Feralolive), current undated profile, “What type of environment does it grow in?”

The commercial-research story describes good drainage, cool winters and hot, dry summers with low humidity as favourable. The WeedWise ecological profile explicitly reports intolerance of waterlogging, despite drought tolerance. Its 400–800 mm observation describes naturalised plants, not commercial yield requirements; it must not become a rainfall cutoff.

**Missing checks:** actual drainage, seasonal moisture/water budget, cultivar chilling and pollination, damaging frost and disease/humidity. No numeric pH method/depth, commercial rainfall floor or chill requirement was verified in these NSW sources. A poor-drainage conflict is supportable with the provenance qualification above, but no current climate/SLGA-only deterministic exclusion is justified.

## Citrus (sweet-orange proxy)

**Sources:** NSW DPI, [Australian mandarin production manual](https://www.dpi.nsw.gov.au/__data/assets/pdf_file/0004/820624/Australian-mandarin-production-manual.pdf), September 2017, “Orchard basics,” pp. 7–11; [dated departmental landing page](https://www.dpird.nsw.gov.au/components/module/accordion/agriculture/horticulture/content/manuals-guides/nsw-dpi-mandarin-manual). Relevant departmental PDF passages retrieved through search; full PDF exceeded browser size limits. NSW DPI, [How to manage soil for citrus](https://www.dpird.nsw.gov.au/agriculture/horticulture/citrus/content/crop-management/orchard-management-factsheets/soil), 17 December 2004.

The manual's general citrus guidance prefers pH **5.5–7.0 by CaCl2**, but this passage does not set one sampling depth. It calls for profile investigation, drainage and rootstock matching; alkaline soils are not universally unsuitable because rootstock and management can allow production. Planting should avoid late-frost exposure. The 2004 citrus page describes an ideal well-structured, drained soil with at least 60 cm topsoil, while acknowledging successful managed production on marginal soils. Its pH wording discusses both water and CaCl2 methods, so the later explicit-method manual is preferable.

**Missing checks:** drainage and effective soil depth, rootstock/scion, salinity, water quality and quantity, orchard frost exposure. Mandarin-specific details must not be silently applied to all sweet oranges. A known poor-drainage constraint is defensible; a hard PHW limit or clay-percentage exclusion is not.

## Improved pasture (perennial ryegrass proxy)

**Sources:** NSW DPIRD, [Perennial ryegrass](https://www.dpird.nsw.gov.au/agriculture/pastures-and-rangelands/species-varieties/pf/factsheets/perennial-ryegrass), undated Agnote-derived webpage; NSW DPI, [Annual, Italian and short rotation ryegrass varieties 2010](https://www.dpird.nsw.gov.au/agriculture/pastures-and-rangelands/species-varieties/rygrass-varieties), March 2010, Primefact 1002; NSW Government/LLS, [Seasonal pasture management](https://www.nsw.gov.au/regional-and-primary-industries/agriculture/pastures/seasonal-pasture), current undated webpage.

The perennial-ryegrass page gives region-specific annual-rainfall minima: 700 mm southern, 800 mm northern and 900 mm coastal. Cool summers and evenly distributed rain favour persistence; shallow roots give low drought tolerance, and aluminium may restrict roots. No numeric pH method/depth is given. Primefact 1002 warns of poor persistence from hot summers and tropical-grass competition on the far north coast and southern irrigation areas. LLS notes that perennial ryegrass can tolerate short-term waterlogging in cool zones.

**Missing checks:** summer heat/moisture persistence, fertility/aluminium, locally proven cultivar/endophyte, grazing and mixture. Neither all improved pasture nor all climates are represented by perennial ryegrass. Do not infer a regional boundary from latitude or hard-exclude for poor drainage. A region-free floor of 700 mm could only be a conservative literature-screen flag for rainfed perennial ryegrass, not a universal agronomic limit; no such implementation is recommended without regional/water-context work.

## Recommended model disposition

No new hard pH/texture/carbon or annual-temperature exclusions are supported for these eight crops using the current inputs. Retain rice's explicit rainfed demo exclusion. Prefer crop-specific missing checks and dated sources. If drainage is supplied by a user, distinguish a reported conflict from modelled measurement and from permanent crop impossibility; unknown drainage must remain unknown. Regional rainfall minima and phenology-based risks should be contextual evidence until compatible inputs and regional definitions exist.
