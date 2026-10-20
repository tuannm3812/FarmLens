"""Create self-contained print/share sources from the finished local interface."""

import base64
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def data(path: str, mime: str) -> str:
    """Embed a repository asset without requiring network access when rendering."""
    encoded = base64.b64encode((ROOT / path).read_bytes()).decode()
    return f"data:{mime};base64,{encoded}"


def document(title: str, style: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        f"<title>{title}</title><style>{BASE}{style}</style><body>{body}</body></html>"
    )


BASE = f"""
@font-face{{font-family:Inter;src:url('{data("web/fonts/inter-latin.woff2", "font/woff2")}');font-weight:100 900}}
@font-face{{font-family:Manrope;src:url('{data("web/fonts/manrope-latin.woff2", "font/woff2")}');font-weight:100 900}}
*{{box-sizing:border-box}}body{{margin:0;color:#253c31;background:#f7f4eb;font:16px/1.5 Inter,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
h1,h2,h3,p{{margin:0}}h1,h2,h3{{font-family:Manrope,sans-serif}}a{{color:inherit}}.tag{{font-size:12px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase}}
.brand{{display:flex;align-items:center;gap:16px}}.brand img{{width:60px;height:60px}}.brand strong{{font:800 36px Manrope;letter-spacing:-1.5px}}.muted{{color:#657063}}
"""
logo = data("web/assets/icons/brand.svg", "image/svg+xml")
finn = data("web/assets/brand/finn.svg", "image/svg+xml")
explorer = data("docs/screenshots/showcase-explorer.png", "image/png")
crops = data("docs/screenshots/showcase-crops.png", "image/png")
brand = f'<div class="brand"><img src="{logo}" alt="FarmLens logo"><strong>FarmLens</strong></div>'
credits = (
    'Sources: Open-Meteo · CSIRO/TERN SLGA · FAO EcoCrop · NSW guidance · '
    'Geoscience Australia DEA · NSW Spatial Services. '
    'Map © OpenStreetMap contributors (ODbL); boundary © ABS (CC BY 4.0).'
)

poster_style = """
@page{size:A3 landscape;margin:0}.poster{width:420mm;height:297mm;padding:13mm 15mm;position:relative;overflow:hidden}
header{display:flex;justify-content:space-between;align-items:center}.edition{text-align:right;font-size:12px;color:#657063}
h1{padding-bottom:8px;font-size:46px;line-height:1.25;letter-spacing:-1.8px;margin:22px 0 9px;max-width:1150px}.pitch{font-size:19px;color:#657063}
.main{display:grid;grid-template-columns:850px 1fr;gap:30px;margin-top:27px}.screen{width:100%;border:1px solid #d9dacd;border-radius:15px;display:block;box-shadow:0 6px 22px #203f3211}.caption{font-size:11px;color:#657063;margin-top:10px}
.guide{background:#eee7c7;border-radius:18px;padding:23px}.guide-title{display:flex;align-items:center;gap:14px;margin-bottom:14px}.guide img{width:75px;height:75px}.guide h2{font-size:29px;letter-spacing:-1px}.guide p{font-size:14px;line-height:1.7}
.feature{border-top:1px solid #cdd1c3;margin-top:22px;padding-top:18px}.feature .tag{font-size:10px;color:#66735c}.feature h3{font-size:19px;margin:6px 0}.feature p{font-size:13px;line-height:1.7;color:#657063}
.trust{display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;margin-top:24px;border-top:3px solid #e7bd45;padding-top:16px}
.trust h3{font-size:17px;margin-bottom:6px}.trust p{font-size:12px;color:#657063;line-height:1.6}
footer{position:absolute;bottom:11mm;left:15mm;right:15mm;display:flex;justify-content:space-between;gap:35px;border-top:1px solid #d9dacd;padding-top:13px}
footer p{font-size:9px;max-width:880px;color:#657063;line-height:1.6}footer strong{font-size:14px;text-align:right;max-width:330px}
"""
poster_body = f"""
<main class="poster">
<header>{brand}<p class="edition">YOUR FARMING COMPANION<br>Local NSW showcase · 20 October 2026</p></header>
<h1>A clearer starting point for your land.</h1>
<p class="pitch">Your land, your climate, your best crops, with the reasons.</p>
<div class="main"><section><img class="screen" src="{crops}" alt="Recorded Dubbo crop options with transparent screening scores">
<p class="caption">Recorded Dubbo demo · 15 crop profiles · scores are screening indices, not success probabilities.</p></section>
<aside><div class="guide"><div class="guide-title"><img src="{finn}" alt="Finn, the illustrated report guide"><div><span class="tag">Ask FarmLens</span><h2>Meet Finn.</h2></div></div>
<p>A friendly guide to the report. Explore why a crop appears, what to watch and which assumptions need checking.</p>
<p style="margin-top:12px;font-size:11px">Supported local questions. Optional model-written crop explanations are a separate feature.</p></div>
<section class="feature"><span class="tag">01 / Understand the place</span><h3>Land, soil and weather</h3><p>Modelled Australian soil, dated imagery and weather, with source status visible.</p></section>
<section class="feature"><span class="tag">02 / Inspect the reasoning</span><h3>Every score has a reason</h3><p>Explicit environmental ranges, factor bars and source-linked NSW checks.</p></section>
<section class="feature"><span class="tag">03 / Explore the assumptions</span><h3>Water and budget scenarios</h3><p>Separate tools for historical water gaps and editable gross margins.</p></section></aside></div>
<div class="trust"><section><h3>Built to make uncertainty visible.</h3><p>Unknown and unavailable data stay labelled. Imagery is dated context; soil values are modelled.</p></section>
<section><h3>Python engine. Custom web UI.</h3><p>305 Python + 43 JavaScript checks passed. Local caching and bounded requests support the showcase.</p></section>
<section><h3>Next: learn with local experts.</h3><p>Weights and scenarios remain uncalibrated. Seek agronomist review and compare with field measurements.</p></section></div>
<footer><p>{credits}<br>Original FarmLens SVG identity; Inter and Manrope under SIL OFL. Full evidence and credits accompany this poster. No public demo is deployed.</p>
<strong>Indicative only.<br>Check with a local agronomist.</strong></footer>
</main>"""
(OUT / "farmlens-showcase-2026-10-20.html").write_text(
    document("FarmLens · local showcase", poster_style, poster_body)
)

social_style = """
.social{width:1200px;height:1500px;padding:54px 60px;position:relative;overflow:hidden}
header{display:flex;justify-content:space-between;align-items:center}.pill{font-size:13px;padding:10px 14px;border:1px solid #d6d2bd;border-radius:22px}
h1{padding-bottom:8px;font-size:68px;line-height:1.2;letter-spacing:-3px;margin:40px 0 17px;max-width:1000px}.lead{font-size:23px;color:#657063;max-width:920px;line-height:1.5}
.screen{display:block;width:1080px;height:auto;margin-top:32px;border:1px solid #d6d8cb;border-radius:15px;box-shadow:0 12px 30px #25453415}
.caption{font-size:12px;color:#657063;margin-top:12px}
.bottom{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin-top:28px;padding-top:21px;border-top:3px solid #e7bd45}
.bottom h2{font-size:20px;letter-spacing:-.4px;margin-bottom:6px}.bottom p{font-size:15px;color:#657063;line-height:1.6}
.finn{display:flex;gap:12px}.finn img{width:58px;height:58px;flex-shrink:0}
footer{position:absolute;bottom:42px;left:60px;right:60px;border-top:1px solid #d6d8cb;padding-top:17px;display:flex;align-items:flex-end;justify-content:space-between;gap:30px}
footer p{font-size:10px;max-width:690px;color:#657063;line-height:1.7}footer strong{font-size:13px;max-width:270px;text-align:right}
"""
social_body = f"""
<main class="social"><header>{brand}<span class="pill">NSW · Local prototype</span></header>
<h1>A clearer starting point<br>for your land.</h1>
<p class="lead">Explore crop possibilities, understand the reasons,<br>and see what needs a closer look.</p>
<img class="screen" src="{explorer}" alt="Recorded FarmLens explorer showing Dubbo soil, imagery and weather">
<p class="caption">Recorded Dubbo demo · 20 October 2026 · imagery shows its survey date.</p>
<div class="bottom"><section><h2>Know the context.</h2><p>Climate, modelled soil and dated land imagery.</p></section>
<section><h2>Follow the reasons.</h2><p>Crop factors, local checks and editable scenarios.</p></section>
<section class="finn"><img src="{finn}" alt="Finn"><div><h2>Ask Finn.</h2><p>A friendly guide to your report.</p></div></section></div>
<footer><p>{credits}<br>Screening prototype. No yield or profit prediction. Full credits in the accompanying project notes.</p><strong>Indicative only.<br>Check with a local agronomist.</strong></footer></main>"""
(OUT / "farmlens-linkedin.html").write_text(
    document("FarmLens · LinkedIn showcase", social_style, social_body)
)

script = (OUT / "showcase-demo-script.md").read_text()
main_script = script.split("## Three-minute walkthrough\n", 1)[1].split("## 60-second backup", 1)[0]
sections = []
for chunk in main_script.split("\n### ")[1:]:
    heading, content = chunk.split("\n\n", 1)
    cue, speech = content.strip().split("\n\n", 1)
    speech_text = html.escape(re.sub(r"\s+", " ", speech).strip())
    sections.append(
        f'<section class="segment"><h3>{html.escape(heading)}</h3>'
        f'<p class="cue">{html.escape(cue.replace("**", ""))}</p>'
        f'<p>{speech_text}</p></section>'
    )
backup = script.split("## 60-second backup\n", 1)[1].split("## Before recording", 1)[0].strip()
handout_style = """
@page{size:A4;margin:0}.page{position:relative;width:210mm;height:297mm;padding:15mm 17mm 19mm;break-after:page;overflow:hidden}.page:last-child{break-after:auto}
.page .brand img{width:35px;height:35px}.page .brand strong{font-size:24px}h1{font-size:27px;letter-spacing:-.8px;margin:16px 0 7px}.sub{font-size:11px;color:#657063}
.segment{border-top:1px solid #d5d5c7;margin-top:14px;padding-top:10px}.segment h3{font-size:14px}.segment p{font-size:12px;line-height:1.6;margin-top:6px}.segment .cue{font-size:10px;line-height:1.5;color:#316b83}
.foot{position:absolute;bottom:11mm;left:17mm;right:17mm;display:flex;justify-content:space-between;border-top:1px solid #d5d5c7;padding-top:8px;font-size:9px;color:#657063}
.backup{font-size:14px;line-height:1.9;margin-top:22px}.box{border-left:4px solid #e7bd45;background:#fff;padding:16px 20px;margin:24px 0;font-size:13px;line-height:1.8}
h2{font-size:19px;margin:24px 0 9px}.notes{font-size:12px;line-height:1.8}.notes li{margin:7px 0}ul,ol{padding-left:20px}
"""
handout_body = f"""
<article class="page">{brand}<h1>The three-minute walkthrough</h1><p class="sub">Home → Land → Weather → Crops → Finn → Scenarios. Keep Dubbo prepared; timings include clicks.</p>
{''.join(sections)}<footer class="foot"><span>FarmLens · Local showcase · 20 October 2026</span><span>1 / 2</span></footer></article>
<article class="page">{brand}<h1>The 60-second backup</h1><p class="backup">{html.escape(backup)}</p>
<h2>Before you present</h2><ol class="notes"><li>Start the local server and open Home at 127.0.0.1:8503.</li><li>Prepare Dubbo using cached data. Confirm the forecast dates and imagery status; browser map tiles and imagery may still need internet.</li><li>Open Finn once. Use the recorded screenshots if a request takes more than five seconds, and call them recorded examples.</li><li>Keep the default water/budget tools as demonstrations of assumptions. Do not describe archived prices as current returns.</li></ol>
<h2>If someone asks about reliability</h2><ul class="notes"><li>Soil values are modelled; the imagery is dated context.</li><li>Scores are provisional indices, not success probabilities or yield forecasts.</li><li>Finn is a bounded local report guide. Optional OpenAI crop wording is separate.</li><li>305 Python and 43 JavaScript tests passed. Those checks establish software behavior, not agronomic accuracy.</li></ul>
<div class="box"><strong>Indicative only. Check with a local agronomist.</strong><br>Next: agronomist review and comparison with field measurements.</div>
<p class="notes muted">Full script, recording cues, source credits and fallback images accompany this handout in showcase-demo-script.md and showcase-release-notes.md.</p>
<footer class="foot"><span>FarmLens · Local showcase · 20 October 2026</span><span>2 / 2</span></footer></article>
"""
(OUT / "showcase-demo-script.html").write_text(
    document("FarmLens · speaking script", handout_style, handout_body)
)
print("Wrote poster, social image and two-page handout HTML sources.")
