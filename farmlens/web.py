"""Local custom UI: python -m farmlens.web. Never bind this demo publicly."""
import argparse
import hashlib
from dataclasses import asdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from farmlens.config import CACHE_DIR, ROOT, PRESETS, SCORE_WEIGHTS, TIMEZONE
from farmlens.explain import explain
from farmlens.fire import FireClient
from farmlens.geocode import Geocoder
from farmlens.land_cover import LandCoverClient
from farmlens.imagery import ImageryClient
from farmlens.vegetation import VegetationClient
from farmlens.budget import assess_budget, budget_metadata
from farmlens.location import boundary, in_nsw
from farmlens.scoring import load_crops, recommend
from farmlens.service import load_point
from farmlens.agronomy import DRAINAGE_OPTIONS
from farmlens.water import assess_water, validate_water_inputs, water_metadata
from farmlens.water_climate import WaterClimateClient


class RequestError(ValueError):
    """Only deliberate, non-sensitive messages may be returned to the browser."""



def validate_scenario(payload):
    if not isinstance(payload, dict):
        raise RequestError("Expected a location and scenario")
    lat, lon = payload.get("lat"), payload.get("lon")
    if isinstance(lat,bool) or isinstance(lon,bool) or not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)) or not in_nsw(lat,lon):
        raise RequestError("Choose a point on land inside NSW; the ACT is outside this demo.")
    drainage = payload.get("drainage", "unknown")
    if drainage not in DRAINAGE_OPTIONS:
        raise RequestError("Choose a valid drainage description")
    mode, month = payload.get("mode","explore"), payload.get("month",5)
    irrigation, category = payload.get("irrigation","rainfed"), payload.get("category")
    if mode not in ("explore","season") or type(month) is not int or not 1<=month<=12:
        raise RequestError("Choose a valid mode and planting month")
    if irrigation not in ("rainfed","irrigated") or category not in (None,"annual","perennial","pasture"):
        raise RequestError("Invalid water scenario or crop category")
    for key in ("cache_only","refresh","load_fire"):
        if key in payload and type(payload[key]) is not bool:
            raise RequestError("Invalid data preference")
    return {"lat":lat,"lon":lon,"mode":mode,"month":month,"irrigation":irrigation,"category":category,"drainage":drainage,
            **{key:payload.get(key,False) for key in ("cache_only","refresh","load_fire")}}


def dispatch(path, payload, cache_dir=CACHE_DIR):
    if path == "/api/search":
        query=payload.get("query") if isinstance(payload,dict) else None
        if not isinstance(query,str) or not 2<=len(query.strip())<=250:
            raise RequestError("Enter a public place or address, between 2 and 250 characters")
        return asdict(Geocoder(cache_dir).search(query.strip()))
    if path not in ("/api/analyze","/api/explain","/api/water","/api/reverse","/api/land-cover","/api/budget","/api/vegetation","/api/imagery"):
        raise RequestError("Unknown request")
    point=validate_scenario(payload)
    if path == "/api/imagery":
        return asdict(ImageryClient(cache_dir, cache_only=point["cache_only"])
                      .fetch(point["lat"], point["lon"], refresh=point["refresh"]))
    if path == '/api/budget':
        try:
            return assess_budget(payload)
        except ValueError as exc:
            raise RequestError(str(exc)) from exc
    if path == '/api/vegetation':
        return asdict(VegetationClient(cache_dir, cache_only=point['cache_only'] and not point['refresh'])
                      .fetch(point['lat'], point['lon'], refresh=point['refresh']))
    if path == '/api/land-cover':
        return asdict(LandCoverClient(cache_dir, cache_only=point['cache_only'] and not point['refresh'])
                      .fetch(point['lat'], point['lon'], refresh=point['refresh']))
    if path == '/api/reverse':
        return asdict(Geocoder(cache_dir,cache_only=point['cache_only']).reverse(point['lat'],point['lon']))
    today=datetime.now(ZoneInfo(TIMEZONE)).date()
    if path == "/api/water":
        try:
            inputs = validate_water_inputs(payload)
        except ValueError as exc:
            raise RequestError(str(exc)) from exc
        history = WaterClimateClient(cache_dir, today=today,
            cache_only=point["cache_only"] and not point["refresh"]).history(point["lat"],point["lon"],refresh=point["refresh"])
        source = {key:value for key,value in asdict(history).items() if key != "data"}
        source["grid"] = history.data.get("grid")
        return {"source":source,"assessment":assess_water(history,inputs)}
    data=load_point(point["lat"],point["lon"],cache_dir=cache_dir,
                    cache_only=point["cache_only"] and not point["refresh"],refresh=point["refresh"],today=today)
    fire=FireClient(cache_dir,cache_only=not point["load_fire"],today=today).fetch(
        point["lat"],point["lon"],max_seconds=20 if point["load_fire"] else None)
    result=recommend(load_crops(),data["climate"],data["soil"],mode=point["mode"],
                     planting_month=point["month"] if point["mode"]=="season" else None,
                     irrigation=point["irrigation"],drainage=point["drainage"],category=point["category"] if point["mode"]=="explore" else None,
                     fire_exposure=fire.data["exposure"])
    if fire.stale:
        result["evidence_quality"]="provisional — stale fire data"
    # Bind to evidence state, not incidental refresh/cache warning wording.
    evidence = {name: {"stale": value.stale, "offline": value.status == "offline",
                       "source": value.source, "fetched_at": value.fetched_at}
                for name, value in {**data, "fire": fire}.items()}
    fingerprint=hashlib.sha256(json.dumps({"shortlist":result["top_three"],
        "quality":result["evidence_quality"],"evidence":evidence},
        sort_keys=True,allow_nan=False).encode()).hexdigest()
    if path=="/api/explain":
        if payload.get("fingerprint") != fingerprint:
            raise RequestError("The shortlist changed; refresh the report before explaining it")
        return {"explanation":explain(result,cache_dir=cache_dir),"result":result}
    return {"point":point,"data":{k:asdict(v) for k,v in {**data,"fire":fire}.items()},
            "result":result,"weights":SCORE_WEIGHTS,"model_version":"soil-screen-v3-nsw-checks","fingerprint":fingerprint}


def same_origin(origin, host, port):
    hosts={f"127.0.0.1:{port}",f"localhost:{port}"}
    return host in hosts and origin in (None,f"http://{host}")


def render_page(filename, active):
    """Render a fixed local page with one shared, script-independent navigation."""
    nav = (ROOT/'web'/'navigation.html').read_text()
    for name in ('home','explore','about'):
        nav = nav.replace('{{'+name+'_current}}', 'aria-current="page"' if name == active else '')
    return (ROOT/'web'/filename).read_text().replace('<!-- site-navigation -->',nav).encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Do not log address searches or coordinates.

    def send(self, status, payload, content_type="application/json; charset=utf-8"):
        content=json.dumps(payload,allow_nan=False).encode() if not isinstance(payload,bytes) else payload
        self.send_response(status)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(content)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options","DENY")
        self.end_headers()
        try:self.wfile.write(content)
        except (BrokenPipeError,ConnectionResetError):pass

    def do_GET(self):
        if not same_origin(None,self.headers.get("Host"),self.server.server_port):
            return self.send(403,{"error":"Local access only"})
        if self.path=="/api/bootstrap":
            return self.send(200,{"presets":[{"name":n,"lat":p[0],"lon":p[1]} for n,p in PRESETS.items()],
                                  "fire_configured":bool(os.getenv("FIRMS_MAP_KEY")),"water":water_metadata(),"budget":budget_metadata()})
        if self.path=="/api/boundary":
            return self.send(200,boundary())
        pages={'/':('home.html','home'),'/explore':('index.html','explore'),
               '/explore/':('index.html','explore'),'/index.html':('index.html','explore'),
               '/about':('about.html','about'),'/about/':('about.html','about')}
        if self.path in pages:
            try:
                return self.send(200,render_page(*pages[self.path]),'text/html; charset=utf-8')
            except OSError:
                return self.send(503,{'error':'Page unavailable'})
        assets={"/app.js":("app.js","text/javascript"),"/style.css":("style.css","text/css"),
                "/imagery.js":("imagery.js","text/javascript"),
                "/companion.js":("companion.js","text/javascript"),
                "/companion.css":("companion.css","text/css"),
                "/site.css":("site.css","text/css"),"/navigation.js":("navigation.js","text/javascript"),
                "/comparison.js":("comparison.js","text/javascript"),
                "/presentation.js":("presentation.js","text/javascript"),
                "/water.js":("water.js","text/javascript"),
                "/budget.js":("budget.js","text/javascript"),
                "/vegetation.js":("vegetation.js","text/javascript"),
                "/insights.css":("insights.css","text/css"),
                "/location.js":("location.js","text/javascript"),
                "/overview.js":("overview.js","text/javascript"),
                "/overview.css":("overview.css","text/css"),
                "/assets/crops/manifest.json":("assets/crops/manifest.json","application/json"),
                "/assets/icons/crops.svg":("assets/icons/crops.svg","image/svg+xml"),
                "/assets/icons/brand.svg":("assets/icons/brand.svg","image/svg+xml"),
                "/assets/brand/finn.svg":("assets/brand/finn.svg","image/svg+xml"),
                "/assets/brand/wordmark.svg":("assets/brand/wordmark.svg","image/svg+xml"),
                "/assets/brand/mark-mono.svg":("assets/brand/mark-mono.svg","image/svg+xml"),
                "/assets/icons/land.svg":("assets/icons/land.svg","image/svg+xml"),
                "/assets/land-cover/preview.html":("assets/land-cover/preview.html","text/html"),
                "/fonts/inter-latin.woff2":("fonts/inter-latin.woff2","font/woff2"),
                "/fonts/manrope-latin.woff2":("fonts/manrope-latin.woff2","font/woff2")}
        # Fixed catalogue; never interpret request paths or manifest values as filesystem paths.
        crop_ids=("wheat","barley","canola","oats","chickpea","lentil","sorghum","cotton",
                  "rice","lucerne","grapes","olives","citrus","macadamia","improved_pasture")
        assets.update({f"/assets/crops/{crop}.jpg":(f"assets/crops/{crop}.jpg","image/jpeg") for crop in crop_ids})
        land_art=("cultivated","natural","aquatic","built","bare","water","unknown")
        assets.update({f"/assets/land-cover/{kind}.svg":(f"assets/land-cover/{kind}.svg","image/svg+xml") for kind in land_art})
        if self.path not in assets:
            return self.send(404,{"error":"Not found"})
        name,mime=assets[self.path]
        try:
            content=(ROOT/"web"/name).read_bytes()
        except OSError:
            return self.send(404,{"error":"Asset unavailable"})
        return self.send(200,content,mime if mime.startswith(("font/","image/")) else mime+"; charset=utf-8")

    def do_POST(self):
        if not same_origin(self.headers.get("Origin"),self.headers.get("Host"),self.server.server_port):
            return self.send(403,{"error":"Same-origin local requests only"})
        if self.headers.get("Content-Type","").split(";")[0]!="application/json":
            return self.send(415,{"error":"JSON requests required"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 0<size<=16384:
                return self.send(413,{"error":"Invalid request size"})
            self.connection.settimeout(10)
            payload=json.loads(self.rfile.read(size))
            cache_dir=Path(os.getenv("FARMLENS_CACHE_DIR") or CACHE_DIR)
            return self.send(200,dispatch(self.path,payload,cache_dir))
        except RequestError as exc:
            return self.send(400,{"error":str(exc)})
        except (ValueError,TypeError):
            return self.send(400,{"error":"Invalid request. Select a NSW land point and a valid scenario."})
        except Exception:
            return self.send(503,{"error":"This request could not complete. Try a cached preset or try again."})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=8503)
    args=parser.parse_args()
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    print(f"FarmLens custom app: http://127.0.0.1:{args.port}/",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=="__main__":main()
