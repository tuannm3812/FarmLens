"""Small, local UI assets: monochrome outline icons and a quiet field palette."""
import html
import base64
from pathlib import Path

PATHS = {
    "land": '<path d="M3 18 12 3l9 15H3Z"/><path d="m7 18 5-8 5 8M10 18l2-3 2 3"/>',
    "pin": '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    "soil": '<path d="m3 7 9-4 9 4-9 4-9-4Zm0 5 9 4 9-4M3 17l9 4 9-4"/>',
    "rain": '<path d="M6 14a4 4 0 1 1 0-8 6 6 0 0 1 11-1 4.5 4.5 0 0 1 1 9M8 17l-1 3m6-3-1 3m6-3-1 3"/>',
    "temp": '<path d="M9 14.5V5a3 3 0 0 1 6 0v9.5a5 5 0 1 1-6 0ZM12 8v10"/><path d="M18 5h3m-3 4h2"/>',
    "frost": '<path d="M12 2v20M3.3 7l17.4 10M3.3 17 20.7 7M9 4l3 3 3-3M9 20l3-3 3 3M4 10l4-1-1-4m10 14-1-4 4-1M4 14l4 1-1 4m10-14-1 4 4 1"/>',
    "crop": '<path d="M12 22V5m0 7C7 12 4 9 4 5c5 0 8 3 8 7Zm0 6c5 0 8-3 8-7-5 0-8 3-8 7Zm0-11c4 0 6-2 6-6-4 0-6 2-6 6Z"/>',
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "check": '<path d="m5 12 4 4L19 6"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h10"/>',
}


def icon(name, size=22):
    return (f'<svg class="mono-icon" width="{size}" height="{size}" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{PATHS[name]}</svg>')


def heading(label, name, kicker):
    return f'<div class="section-heading">{icon(name)}<div><div class="eyebrow">{html.escape(kicker)}</div><h3>{html.escape(label)}</h3></div></div>'


def metric(label, value, name):
    return f'<div class="land-metric"><span>{icon(name,18)} {html.escape(label)}</span><strong>{html.escape(value)}</strong></div>'


STYLE = """<style>
.stApp {background:#f7f8f4;}
.block-container {max-width:1360px;padding:4.5rem 2.4rem 3rem;}
[data-testid="stSidebar"] {background:#eef1e9;border-right:1px solid #dbe1d7;}
[data-testid="stSidebar"] .block-container {padding-top:1.5rem;}
h1 {font-size:3rem!important;letter-spacing:-.065em;line-height:1.1!important;color:#1d392d;}
h2,h3 {letter-spacing:-.035em;color:#233e31;}
.mono-icon {vertical-align:middle;flex-shrink:0;}
.brand {display:flex;align-items:center;gap:10px;font-size:1.4rem;font-weight:700;letter-spacing:-.04em;margin-bottom:6px;}
.brand-mark {display:inline-flex;border:1px solid #8b9d88;border-radius:9px;padding:7px;}
.eyebrow {font-size:.67rem;letter-spacing:.15em;font-weight:650;color:#59705f;line-height:1.4;}
.hero-top {display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;gap:12px;}
.edition {border:1px solid #d2dccf;border-radius:30px;padding:5px 10px;color:#516650;font-size:.68rem;white-space:nowrap;}
.intro {font-size:1.12rem;color:#53695b;max-width:720px;margin:.25rem 0 1.6rem;line-height:1.6;}
.section-heading {display:flex;gap:12px;align-items:center;margin:1.2rem 0 .8rem;color:#48674f;}
.section-heading h3 {margin:2px 0 0;padding:0;font-size:1.2rem!important;line-height:1.4;}
.land-metrics {display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;}
.land-metric {border:1px solid #dfe5db;background:#fff;border-radius:12px;padding:14px 15px;}
.land-metric span {display:flex;align-items:center;gap:7px;font-size:.73rem;color:#5c6c60;}
.land-metric strong {display:block;margin-top:9px;font-size:1.65rem;font-weight:600;letter-spacing:-.05em;color:#233e31;}
.evidence {display:flex;gap:9px;align-items:center;border:1px solid #d5dfd0;border-radius:9px;background:#ecf2e7;padding:10px 12px;margin:10px 0;font-size:.76rem;color:#36573d;}
.score {font-size:3.2rem;font-weight:650;letter-spacing:-.065em;line-height:1.1;margin:10px 0 16px;}
.score small {font-size:.9rem;color:#708072;letter-spacing:0;font-weight:400;}
.crop-title {display:flex;align-items:center;gap:10px;font-size:1.35rem;font-weight:650;line-height:1.3;}
.factor {background:#f0f3eb;border-left:2px solid #6c8461;border-radius:0 7px 7px 0;padding:.7rem .8rem;font-size:.79rem;margin:.9rem 0;line-height:1.5;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.crop-title) {background:#fff;border-radius:14px;}
[data-testid="stProgress"] p {font-size:.76rem;}
[data-testid="stProgress"] [role="progressbar"] {height:5px;}
[data-testid="stExpander"] {background:#fff;border-radius:10px;}
button {border-radius:8px!important;}
iframe[title="streamlit_folium.st_folium"] {border-radius:12px;border:1px solid #d5ddd0;}
@media(max-width:1100px) {
 .block-container {padding:4.5rem 1.4rem 2rem;}
 [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.land-metrics) {flex-wrap:wrap;}
 [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.land-metrics)>div[data-testid="stColumn"] {min-width:100%;flex:1 1 100%;}
 .crop-title {font-size:1.1rem;}
}
@media(max-width:640px) {
 .block-container {padding:4.5rem 1rem 1.5rem;}
 h1 {font-size:2.5rem!important;}
 .edition {display:none;}
 .land-metric {padding:12px;}
 .land-metric strong {font-size:1.4rem;}
}
</style>"""


# Bundle typography in the document so Streamlit needs no external font request.
_FONT_DIR = Path(__file__).resolve().parents[1] / "web" / "fonts"
_FONT_CSS = "".join(
    "@font-face{font-family:'" + family + "';font-style:normal;font-weight:" + weights
    + ";font-display:swap;src:url(data:font/woff2;base64,"
    + base64.b64encode((_FONT_DIR / name).read_bytes()).decode("ascii") + ") format('woff2')}"
    for family, name, weights in [("Inter", "inter-latin.woff2", "400 700"),
                                  ("Manrope", "manrope-latin.woff2", "500 800")]
)
STYLE += "<style>" + _FONT_CSS + """
.stApp {background:#f7f4eb;color:#252a26;font-family:Inter,-apple-system,sans-serif;}
[data-testid="stSidebar"] {background:#efeadc;border-color:#dedacd;}
[data-testid="stMarkdownContainer"],input,textarea,select,button {font-family:Inter,-apple-system,sans-serif;}
h1,h2,h3,.brand,.crop-title {font-family:Manrope,Inter,sans-serif!important;color:#252a26;}
.brand-mark {background:#e7b83c;color:#252a26;border-color:#a77d18;}
.eyebrow,.intro,.edition,.land-metric span,.score small {color:#62665d;}
.land-metric {border-color:#dedacd;}.land-metric strong {color:#252a26;font-variant-numeric:tabular-nums;}
.land-metric .mono-icon {color:#316b83;}.section-heading {color:#355b48;}
.evidence {background:#eaf0e9;border-color:#c8d5c9;color:#355b48;}
.factor {background:#fff0e8;border-color:#a5442d;color:#8a3825;}
.score {font-variant-numeric:tabular-nums;color:#252a26;}
[data-testid="stBaseButton-primary"] {background:#e7b83c;color:#252a26;border-color:#a77d18;}
[data-testid="stBaseButton-primary"] p {color:#252a26;}
[data-testid="stProgress"] [role="progressbar"] > div {background:#355b48;}
a {color:#316b83;}
</style>"""
