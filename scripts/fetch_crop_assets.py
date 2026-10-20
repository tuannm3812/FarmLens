"""Refresh curated, licensed Wikimedia photos; never called by the running app.

Run from the repo with .venv/bin/python scripts/fetch_crop_assets.py.
Review any changed source metadata and photographs before distributing them.
"""
import hashlib
import html
import json
from pathlib import Path
import re
import time
import sys

import requests

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "web" / "assets" / "crops"
SELECTION = {
    "wheat": ("Vehnäpelto 6.jpg", "Wheat heads growing in a field", "Grain"),
    "barley": ("Barley (Hordeum vulgare) - United States National Arboretum - 24 May 2009.jpg", "Barley heads with long awns", "Grain"),
    "canola": ("Canola field temora nsw.jpg", "A field of flowering yellow canola", "Oilseed"),
    "oats": ("AvenaSativa3.jpg", "Oat stems and seed heads", "Grain"),
    "chickpea": ("Starr-120415-4648-Cicer arietinum-flowers and leaves-Hawea Pl Olinda-Maui (25046161791).jpg", "Chickpea flowers and leaves", "Pulse"),
    "lentil": ("Lentil plants.jpg", "Lentil plants growing outdoors", "Pulse"),
    "sorghum": ("Sorghum bicolor flowerhead1 NWS - Flickr - Macleay Grass Man.jpg", "A sorghum seed head", "Grain"),
    "cotton": ("CottonPlant.JPG", "Cotton bolls on a plant", "Fibre"),
    "rice": ("20201102.Hengnan.Hybrid rice Sanyou-1.6.jpg", "Rice plants growing in a field", "Grain"),
    "lucerne": ("Medicago-sativa-inflorescence.jpg", "Purple lucerne flowers and leaves", "Forage"),
    "grapes": ("Cabernet Sauvignon Gaillac.jpg", "Grape bunches growing on a vine", "Fruit"),
    "olives": ("Olivesfromjordan.jpg", "Olives growing on a leafy branch", "Fruit / oil"),
    "citrus": ("Sapindales - Citrus sinensis - 11.jpg", "Sweet oranges growing on a tree", "Fruit"),
    "macadamia": ("Macadamia integrifolia inflorescences 74 Sunbury St Geebung L1060475.jpg", "Flower clusters on a macadamia tree", "Nut"),
    "improved_pasture": ("Lolium perenne Engels raaigras doorschietend.jpg", "Perennial ryegrass stems and seed heads", "Pasture"),
}


def plain(value):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", value)).split())


def get(session, url, **kwargs):
    for attempt in range(2):
        try:
            response = session.get(url, timeout=(5, 25), **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt:
                raise
            time.sleep(1)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "FarmLens-demo-assets/0.1 (educational local prototype)"
    payload = get(session, "https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": "|".join("File:" + row[0] for row in SELECTION.values()),
        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 960,
    }).json()
    pages = {p["title"]: p for p in payload["query"]["pages"].values()}
    crops = json.loads((DEST / "manifest.json").read_text())["crops"] if (DEST / "manifest.json").exists() else {}
    for crop_id, (filename, alt, use) in SELECTION.items():
        if sys.argv[1:] and crop_id not in sys.argv[1:]:
            continue
        info = pages["File:" + filename]["imageinfo"][0]
        meta = info["extmetadata"]
        licence = meta["LicenseShortName"]["value"]
        if not (licence.startswith("CC BY") or licence in ("CC0", "Public domain")):
            raise ValueError(f"Review unsupported licence: {crop_id}: {licence}")
        url = info.get("thumburl", info["url"]).split("?")[0]
        photo = get(session, url)
        if not photo.content.startswith(b"\xff\xd8\xff"):
            raise ValueError(f"Expected JPEG for {crop_id}")
        if len(photo.content) > 1_500_000:
            raise ValueError(f"Review large asset: {crop_id}")
        (DEST / f"{crop_id}.jpg").write_bytes(photo.content)
        crops[crop_id] = {
            "src": f"/assets/crops/{crop_id}.jpg", "alt": alt, "use": use,
            "title": filename, "creator": {"canola":"John O'Neill (edited by Fir0002)", "grapes":"BerndtF", "cotton":"USDA Natural Resources Conservation Service"}.get(crop_id) or plain(meta.get("Artist", {}).get("value", "Unknown creator")),
            "attribution": plain(meta.get("Attribution", {}).get("value", "")),
            "source_url": info["descriptionurl"], "download_url": url,
            "license": licence, "license_url": meta.get("LicenseUrl", {}).get("value", "").replace("http://", "https://"),
            "description": plain(meta.get("ImageDescription", {}).get("value", "")),
            "width": info.get("thumbwidth", info["width"]), "height": info.get("thumbheight", info["height"]),
            "modifications": "Wikimedia thumbnail; displayed in a cropped frame. Original linked in credit.",
            "sha256": hashlib.sha256(photo.content).hexdigest(),
        }
        print(f"{crop_id}: {licence}, {len(photo.content)//1024} KB", flush=True)
    (DEST / "manifest.json").write_text(json.dumps({"schema": 1, "crops": crops}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
