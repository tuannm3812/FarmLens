"""Run the NSW crop-screening demo with: streamlit run app.py."""
from calendar import month_name
from datetime import datetime
import html
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from farmlens.climate import frost_risk
from farmlens.config import CACHE_DIR, PRESETS, SCORE_WEIGHTS, TIMEZONE
from farmlens.location import boundary, in_nsw
from farmlens.scoring import load_crops, recommend
from farmlens.service import load_point, needs_revalidation
from farmlens.explain import explain
from farmlens.geocode import Geocoder
from farmlens.fire import FireClient

from farmlens.presentation import STYLE, icon, heading, metric

st.set_page_config(page_title="FarmLens · Know your land", page_icon=":material/landscape:", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

if "location" not in st.session_state:
    st.session_state.location = {"name":"Dubbo", "lat":PRESETS["Dubbo"][0], "lon":PRESETS["Dubbo"][1]}
    st.session_state.map_version = 0


def set_location(name, lat, lon):
    previous = st.session_state.location
    changed = lat != previous["lat"] or lon != previous["lon"]
    st.session_state.location = {"name":name, "lat":lat, "lon":lon}
    st.session_state.map_version += 1
    if changed:
        st.session_state.reset_drainage = True
    for key in ("explanation", "point_data", "fire_result"):
        st.session_state.pop(key, None)


def select_preset():
    name = st.session_state.preset
    set_location(name, *PRESETS[name])


def source_label(result):
    text = "OFFLINE DATA" if result.status == "offline" else result.status.upper()
    return text + (" · STALE" if result.stale else "")


def clear_explanation():
    st.session_state.pop("explanation", None)
    st.session_state.pop("explanation_signature", None)


def show_local_checks(crop):
    guidance = crop.get("guidance", {})
    st.write(guidance.get("summary", "Local agronomic checks remain unassessed."))
    labels = {"met":"Check met · not validation", "not_assessed":"Not assessed", "conflict":"Conflict"}
    for check in guidance.get("checks", []):
        st.write(f"**{labels.get(check['status'], 'Not assessed')}** · {check['message']}")
        st.markdown(f"[{check['source_title']}]({check['source_url']})")
    st.caption("Meeting one check does not validate the crop or this location.")


with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">' + icon("land",24) + '</span>FarmLens</div>', unsafe_allow_html=True)
    st.caption("A clearer first look at your land.")
    st.selectbox("Demo location", list(PRESETS), index=1, key="preset", on_change=select_preset)
    st.caption("Or click a point inside NSW on the map.")
    with st.form("address_search"):
        address = st.text_input("Australian place or address", placeholder="e.g. Orange, NSW", max_chars=250)
        submitted = st.form_submit_button("Find address", width="stretch", icon=":material/search:")
    st.caption("Search provided by [OpenStreetMap](https://www.openstreetmap.org/copyright). Submit a public place or address; avoid confidential information.")
    if submitted:
        try:
            with st.spinner("Finding places in NSW…"):
                st.session_state.search_result = Geocoder(Path(os.getenv("FARMLENS_CACHE_DIR") or CACHE_DIR)).search(address)
        except ValueError as exc:
            st.session_state.pop("search_result", None)
            st.warning(str(exc))
    search_result = st.session_state.get("search_result")
    if search_result:
        matches = search_result.data["matches"]
        if search_result.warning:
            st.warning(search_result.warning)
        if matches:
            chosen = st.selectbox("Matching NSW places", range(len(matches)), format_func=lambda i: matches[i]["name"])
            if st.button("Use this location"):
                chosen = matches[chosen]
                set_location(chosen["name"], chosen["lat"], chosen["lon"])
            st.caption(source_label(search_result))
        elif search_result.status != "offline":
            st.info("No NSW matches found. Try adding a town or postcode.")
    st.divider()
    mode = st.radio("What are you exploring?", ["Explore my land", "Plan next season"], key="mode")
    planting_month = None
    if mode == "Plan next season":
        planting_month = st.selectbox("Planting month", list(range(1,13)), index=4,
                                      format_func=lambda m: month_name[m], key="month")
        st.caption("Historical seasonal conditions, not a forecast for a future year.")
    irrigation = st.radio("Water scenario", ["Rainfed", "Irrigated"], horizontal=True, key="irrigation")
    if st.session_state.pop("reset_drainage", False):
        st.session_state.drainage = "unknown"
    drainage_labels = {"unknown":"Unknown", "well_drained":"Well drained", "poorly_drained":"Poorly drained / waterlogging"}
    drainage = st.selectbox("Known drainage (optional)", list(drainage_labels), key="drainage",
                            format_func=drainage_labels.get, on_change=clear_explanation,
                            help="Your observation for this location, not inferred from soil texture. Resets when you change location.")
    category = None
    if mode == "Explore my land":
        choice = st.selectbox("Crop type", ["All crops", "Annual crops", "Perennial crops", "Pasture"], key="category")
        category = {"All crops":None,"Annual crops":"annual","Perennial crops":"perennial","Pasture":"pasture"}[choice]
    st.divider()
    cached_only = st.toggle("Use cached demo data", value=True, key="cached_only",
                            help="No climate or soil network calls. Missing soil pH withholds recommendations; climate fallback is labelled.")
    refresh = st.button("Fetch fresh data", width="stretch", icon=":material/refresh:")
    st.caption("Australian soil maps · selected point only. Missing soil is never replaced with regional guesses.")
    fetch_fire = st.button("Load fire history", disabled=not bool(os.getenv("FIRMS_MAP_KEY")),
                           help="Three full years, within 25 km. A first download can require 220 intervals; repeat to resume if incomplete.")

st.markdown('<div class="hero-top"><div class="eyebrow">NEW SOUTH WALES / FIELD NOTES</div><span class="edition">LAND INTELLIGENCE · DEMO</span></div>', unsafe_allow_html=True)
st.title("FarmLens")
st.markdown('<div class="intro">Your land, your climate, your best crops, with the reasons.</div>', unsafe_allow_html=True)

loc = st.session_state.location
now = datetime.now(ZoneInfo(TIMEZONE))
today = now.date()
cache_dir = Path(os.getenv("FARMLENS_CACHE_DIR") or CACHE_DIR)
point_key = ("slga-v1", loc["lat"], loc["lon"], cached_only, str(cache_dir), today.isoformat())
if (refresh or st.session_state.get("point_key") != point_key or "point_data" not in st.session_state
        or needs_revalidation(st.session_state.get("point_data", {}), now)):
    with st.spinner("Checking climate, soil and the seven-day outlook…"):
        st.session_state.point_data = load_point(loc["lat"], loc["lon"], cache_dir=cache_dir,
                                                cache_only=cached_only and not refresh, refresh=refresh, today=today)
    st.session_state.point_key = point_key
    st.session_state.pop("fire_result", None)
data = st.session_state.point_data
c, s, outlook = data["climate"].data, data["soil"].data, data["forecast"].data
if "fire_result" not in st.session_state or fetch_fire:
    progress = st.progress(0.0, text="Checking complete fire-history coverage…") if fetch_fire else None
    st.session_state.fire_result = FireClient(cache_dir, cache_only=not fetch_fire, today=today).fetch(
        loc["lat"], loc["lon"], max_seconds=20 if fetch_fire else None,
        progress=(lambda value: progress.progress(value, text="Checking complete fire-history coverage…")) if fetch_fire else None)
    if progress is not None:
        progress.empty()
fire = st.session_state.fire_result
data = {**data, "fire":fire}

left, right = st.columns([1.2,1], gap="large")
with left:
    st.markdown(heading("Start with a place", "pin", "01 / YOUR LOCATION"), unsafe_allow_html=True)
    st.caption(f"Selected: {loc['name']} · {loc['lat']:.4f}, {loc['lon']:.4f}")
    map_view = folium.Map(location=[-32.5,147.2], zoom_start=6, tiles="OpenStreetMap", control_scale=True)
    if loc["lon"] > 156:
        map_view.fit_bounds([[loc["lat"]-.15, loc["lon"]-.15],[loc["lat"]+.15,loc["lon"]+.15]])
    else:
        map_view.fit_bounds([[-37.6,140.9],[-28.1,153.7]])
    folium.GeoJson(boundary(), name="New South Wales", style_function=lambda _: {
        "color":"#387254", "weight":1.5, "fillColor":"#76a77c", "fillOpacity":0.09}).add_to(map_view)
    folium.Marker([loc["lat"],loc["lon"]], tooltip=html.escape(loc["name"]),
                  icon=folium.DivIcon(html='<div style="color:#fff;background:#254d37;border:2px solid white;border-radius:50%;padding:6px;box-shadow:0 2px 8px #2345;width:38px;height:38px">'+icon("pin",22)+'</div>',icon_size=(38,38),icon_anchor=(19,19))).add_to(map_view)
    # New component identity clears the previous click after a preset/search selection.
    event = st_folium(map_view, key=f"land_map_{st.session_state.map_version}", height=420,
                      use_container_width=True, returned_objects=["last_clicked"])
    click = (event or {}).get("last_clicked")
    if click:
        lat, lon = click.get("lat"), click.get("lng")
        if in_nsw(lat, lon):
            if abs(float(lat)-loc["lat"]) > 1e-6 or abs(float(lon)-loc["lon"]) > 1e-6:
                set_location("Selected NSW point", float(lat), float(lon))
                st.rerun()
        else:
            st.warning("Choose a point on land inside NSW. The ACT and other states are outside this demo.")
    st.caption("© OpenStreetMap contributors · NSW outline: ABS, CC BY 4.0. Simplified boundary; not a cadastral map.")

with right:
    st.markdown(heading("Your land at a glance", "soil", "02 / THE EVIDENCE"), unsafe_allow_html=True)
    st.caption(f"Climate baseline {c['period']} · soil 0–30 cm")
    ph_text = f"{s['ph']:.1f}" if s.get("ph") is not None else "Unavailable"
    st.markdown('<div class="land-metrics">' +
                metric("Annual rainfall", f"{c['annual_rainfall_mm']:,.0f} mm", "rain") +
                metric("Mean temperature", f"{c['annual_temperature_c']:.1f} °C", "temp") +
                metric("Frost risk · proxy", frost_risk(c["coldest_month_min_c"]).capitalize(), "frost") +
                metric("Soil pH · water", ph_text, "soil") + '</div>', unsafe_allow_html=True)
    st.caption(f"Coldest-month mean minimum {c['coldest_month_min_c']:.1f}°C · driest three months {c['driest_three_months_mm']:.0f} mm. Monthly averages can conceal individual frosts.")
    if s.get("properties") and s.get("ph") is not None:
        st.markdown('<div class="evidence">' + icon("check",18) + ' Australian SLGA · modelled soil · ~90 m grid</div>', unsafe_allow_html=True)
    show_soil = lambda value: "unavailable" if value is None else f"{value:.1f}"
    st.write(f"**Soil texture:** {s['texture']} · {show_soil(s.get('clay_pct'))}% clay, {show_soil(s.get('sand_pct'))}% sand")
    st.caption(f"Organic carbon {show_soil(s.get('soc_g_kg'))} g/kg · depth-weighted 0–30 cm.")
    if s.get("properties"):
        with st.expander("Australian soil evidence", icon=":material/layers:"):
            st.write("CSIRO / TERN Soil and Landscape Grid of Australia. Modelled soil properties, not a field test or today's soil conditions.")
            ph = s["properties"]["ph"]
            if ph.get("lower") is not None:
                st.write(f"pH screening envelope: **{ph['lower']:.1f}–{ph['upper']:.1f}**. A local soil test may change the ranking.")
            st.caption("The envelope averages the layer-specific 5th and 95th bounds by thickness. It is not a joint 90% interval for 0–30 cm. pH is averaged arithmetically as a screening proxy.")
            labels = {"ph":"pH (water)","clay_pct":"Clay (%)","sand_pct":"Sand (%)","soc_g_kg":"Carbon (g/kg)"}
            rows = [{"Property": labels[key], "Depth (cm)": row["depth_cm"], "Modelled": row["value"],
                     "Lower bound":row["lower"], "Upper bound":row["upper"]}
                    for key, prop in s["properties"].items() for row in prop["depths"]]
            if rows:
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            st.caption(f"Queried point: {s['sample_latitude']:.6f}, {s['sample_longitude']:.6f}. Map service release date is not supplied; retrieval date is not a measurement date.")
            for key, prop in s["properties"].items():
                st.markdown(f"[{labels[key]} source layers]({prop['service']}) · {prop['status']} · {prop['fetched_at'] or 'not retrieved'}")
                if prop["warning"]:
                    st.caption(prop["warning"])
    st.write("**Fire exposure:** " + (fire.data["exposure"].capitalize() if fire.data["exposure"] else "Unassessed"))
    st.caption(fire.data["note"])
    with st.container(border=True):
        st.markdown(icon("rain",18) + " **This week**", unsafe_allow_html=True)
        st.write(outlook["note"])
        dates = f" · {outlook['start_date']} to {outlook['end_date']}" if outlook.get("start_date") else ""
        st.caption(source_label(data["forecast"]) + dates)

if cached_only:
    st.caption("CACHED DEMO MODE · Use “Fetch fresh data” to query this point now.")
if data["climate"].status == "offline":
    st.warning("OFFLINE DATA · Climate inputs are regional estimates. Crop scores are provisional.")
if data["soil"].status == "offline":
    st.warning("OFFLINE DATA · Some Australian soil properties are unavailable. Missing pH withholds crop recommendations.")
if any(r.stale for r in data.values()):
    st.warning("Some cached data is stale. Check the source dates below or fetch fresh data.")

result = recommend(load_crops(), data["climate"], data["soil"], mode="season" if planting_month else "explore",
                   planting_month=planting_month, irrigation=irrigation.lower(), category=category,
                   fire_exposure=fire.data["exposure"], drainage=drainage)
if fire.stale:
    result["evidence_quality"] = "provisional — stale fire data"
result["sources"]["fire"] = {"source":fire.source,"status":fire.status,"stale":fire.stale,"fetched_at":fire.fetched_at}
st.divider()
st.markdown(heading("Your crop shortlist", "crop", "03 / OPTIONS TO EXPLORE"), unsafe_allow_html=True)
st.caption("Broad environmental screening · scores out of 100 · not NSW agronomic validation or a probability of success")
if result["ranked"] and not result["has_strong_match"]:
    st.warning("No strong match. The available evidence does not support a suitable crop in this scenario.")
if not result["top_three"]:
    if result.get("guidance_excluded"):
        st.info("No candidates remain after local checks. Review the source-linked guidance exclusions below.")
    else:
        st.info("No eligible crops with sufficient evidence. Check soil pH, monthly climate, crop filters and planting month.")
for warning in result["warnings"]:
    if "Monthly climate" in warning or "Soil pH" in warning:
        st.warning(warning)
if irrigation == "Irrigated":
    st.info("Irrigation supply is unverified. Natural rainfall still determines the rainfall score; a water budget is needed.")

factor_names = {"temperature":"Temperature", "rainfall":"Rainfall", "ph":"Soil pH", "frost":"Frost", "fire":"Fire exposure", "texture":"Soil texture", "carbon":"Carbon condition · proxy"}
cards = st.columns(max(1,len(result["top_three"])), gap="medium")
for rank, (col, crop) in enumerate(zip(cards, result["top_three"]),1):
    with col, st.container(border=True):
        st.caption(f"0{rank} / {crop['category'].upper()}" + (" · PROVISIONAL" if "provisional" in result["evidence_quality"] else ""))
        st.markdown(f'<div class="crop-title">{icon("crop",22)}{html.escape(crop["name"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score">{crop["total"]:.0f}<small> / 100</small></div>', unsafe_allow_html=True)
        st.caption("Local checks required")
        if crop["zero_capped"]:
            st.caption("Absolute limit reached · total capped at 20")
        elif not crop["strong_match"]:
            st.caption("Below the demo’s strong-match threshold")
        for name,value in crop["subscores"].items():
            if value is None:
                st.caption(f"{factor_names[name]} · unassessed")
            else:
                st.progress(max(0.0,min(1.0,value/100)), text=f"{factor_names[name]} · {value:.0f}")
        st.caption("Preferred texture: " + ", ".join(crop["soil_context"]["optimal"]))
        weakest = crop["weakest_factor"]
        message = "No limiting factor among assessed proxies" if crop["subscores"][weakest] == 100 else "Weakest factor: " + factor_names[weakest]
        st.markdown(f'<div class="factor">{message}</div>', unsafe_allow_html=True)
        st.write(crop["notes"])
        with st.expander("Local checks & sources"):
            show_local_checks(crop)
        if crop["season_context"]:
            ctx = crop["season_context"]
            months = ", ".join(month_name[m] for m in ctx["months"])
            st.caption(f"Historical growing months: {months}. {ctx['temperature_c']:.1f}°C · {ctx['rainfall_mm']:.0f} mm · {ctx['frost_days']:.1f} frost days per growing period, averaged across years. Annual rainfall remains the rainfall score input.")
        st.caption(f"[Approximate crop profile]({crop['source_url']})")

if result.get("guidance_excluded"):
    with st.expander(f"Excluded by local guidance ({len(result['guidance_excluded'])})"):
        for crop in result["guidance_excluded"]:
            st.markdown(f"**{crop['name']} · local conflict**")
            st.write(crop["notes"])
            show_local_checks(crop)

signature = hashlib.sha256(json.dumps({"result":result,"drainage":drainage}, sort_keys=True).encode()).hexdigest()
if st.session_state.get("explanation_signature") != signature:
    st.session_state.pop("explanation", None)
if st.button("Explain", key="explain", disabled=not result["top_three"], type="primary", icon=":material/auto_awesome:"):
    with st.spinner("Turning the assessed factors into plain English…"):
        st.session_state.explanation = explain(result, cache_dir=cache_dir)
    st.session_state.explanation_signature = signature
st.caption("Only anonymous crop numbers and scores go to OpenAI when configured. No location or address is sent; the rules always calculate the scores.")
if "explanation" in st.session_state:
    explanation = st.session_state.explanation
    st.caption(f"{explanation['source']} · {explanation['notice']}")
    names = {crop["id"]:crop["name"] for crop in result["top_three"]}
    for entry in explanation["entries"]:
        with st.container(border=True):
            st.markdown(f"**{names[entry['id']]}**")
            st.write(entry["why"])
            st.write("Watch: " + entry["risk"])
            if entry.get("local_cautions"):
                st.markdown("**Local checks · separate from score wording**")
                for caution in entry["local_cautions"]:
                    st.write(caution if isinstance(caution, str) else caution["message"])
    st.caption(explanation["disclaimer"])
with st.expander("How these scores work"):
    st.write("Optimal ranges score 100, declining linearly to zero at absolute limits. Any zero factor caps the weighted total at 20. Missing factors are omitted and the remaining weights are renormalized. Texture scores 100 for preferred classes, 70 for tolerated classes and 40 for unlisted classes. Carbon is a shared condition proxy, with a 5% weight; it is not a nutrient test.")
    st.write("Weights: " + ", ".join(f"{factor_names[k]} {v:.0%}" for k,v in SCORE_WEIGHTS.items()) + ".")
    st.write("Seasonal mode uses historical growing-month temperatures and a broad sowing-month filter. Annual rainfall remains the rainfall score input. Exact dates depend on variety, region, soil moisture and soil temperature.")
    st.write("Drainage, salinity, disease, market access, profitability and cultivar suitability are unassessed. Global crop ranges may produce locally inappropriate candidates, including coastal lentils.")
    st.caption("Fire exposure proxy: fewer than 10 detections = low, 10–99 = medium, 100+ = high over three complete years, using VIIRS S-NPP. These thresholds are uncalibrated; detections are neither distinct fires nor a future fire forecast.")
    st.json(result["excluded"], expanded=False)
with st.expander("Data sources"):
    st.markdown("[Open-Meteo](https://open-meteo.com/) · [Australian SLGA · CSIRO / TERN](https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html) · [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) · [FAO EcoCrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home)")
    st.dataframe(pd.DataFrame([{"Input":key.capitalize(), "Source":r.source, "Status":source_label(r),
                                "Retrieved (UTC)":r.fetched_at or "No observation", "Note":r.warning}
                               for key,r in data.items()]), hide_index=True, width="stretch")
    st.caption("Climate: ERA5 reanalysis. Soil: Australian modelled maps, approximately 90 m grid; no regional soil fallback. The legacy ISRIC SoilGrids client remains available in the package but is not used by the app. Fire is unassessed until historical coverage is available. EcoCrop ranges and scoring weights are approximate and unvalidated for individual farms.")
st.caption("Indicative only. Check with a local agronomist.")
