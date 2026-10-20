"""Numeric-only OpenAI explanations with a deterministic, offline fallback."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from openai import OpenAI, OpenAIError

from farmlens.config import CACHE_DIR

DISCLAIMER = "Indicative only. Check with a local agronomist."
FACTORS = {"temperature":"temperature", "rainfall":"rainfall", "ph":"soil pH", "frost":"frost proxy", "fire":"fire exposure", "texture":"soil texture", "carbon":"organic-carbon condition proxy"}
PROMPT = """Explain these anonymous crop-screening numbers in plain English. Return one why sentence and one risk sentence per index, each under 240 characters. Values are a screening index, not probability or yield. Explain only the supplied numbers; do not infer species, places, management or facts. 100 means an optimal proxy score; 0 is an absolute limit and caps the total at 20. Any null score is unassessed. Texture is a broad crop-preference proxy; carbon is a shared soil-condition proxy, not measured fertility. If strong_match is 0, say it is not a strong match. If offline_or_stale is 1, evidence is provisional. Mention the lowest known sub-score as a risk; if all are 100, mention unassessed drainage or local soil testing. Never claim a crop is safe, profitable, validated or guaranteed. The caller adds a disclaimer."""


def numeric_payload(result):
    """Allowlist numeric fields; never serialize a result or location wholesale."""
    return {"offline_or_stale": int("provisional" in result["evidence_quality"]),
            "seasonal_mode": int(result["mode"] == "season"),
            "planting_month": result.get("planting_month"),
            "irrigated": int(result["irrigation"] == "irrigated"),
            "crops": [{"index":index, "total":crop["total"], "strong_match":int(crop["strong_match"]),
                       "zero_capped":int(crop["zero_capped"]),
                       "subscores":{key:crop["subscores"].get(key) for key in FACTORS},
                       "inputs":{key:crop["inputs"].get(key) for key in ("temperature_c","annual_rainfall_mm","ph","frost_min_c","clay_pct","sand_pct","soc_g_kg")}}
                      for index,crop in enumerate(result["top_three"])]}


def _rules(result):
    entries=[]
    for crop in result["top_three"]:
        assessed={k:v for k,v in crop["subscores"].items() if v is not None}
        best=max(assessed,key=assessed.get)
        weakest=min(assessed,key=assessed.get)
        if not crop["strong_match"]:
            why="This is not a strong match under the assessed environmental limits."
        else:
            why=f"{(FACTORS[best][0].upper()+FACTORS[best][1:])} is a relative strength, scoring {assessed[best]:.0f}/100 in this provisional screen."
        if crop["zero_capped"]:
            risk=f"{(FACTORS[weakest][0].upper()+FACTORS[weakest][1:])} reaches an absolute limit, so the total is capped at 20."
        elif assessed[weakest] == 100:
            risk="Local drainage and soil tests still need checking because these broad proxies do not assess every farm constraint."
        else:
            risk=f"{(FACTORS[weakest][0].upper()+FACTORS[weakest][1:])} is the weakest assessed factor at {assessed[weakest]:.0f}/100 and needs local checking."
        entries.append({"id":crop["id"],"why":why,"risk":risk,
                        "local_cautions":[check["message"] for check in crop.get("guidance",{}).get("checks",[])
                                          if check["status"] != "met"]})
    return entries


def _validated(payload, count):
    rows=payload["crops"]
    if len(rows)!=count or {r["index"] for r in rows} != set(range(count)):
        raise ValueError("Missing, duplicate or unknown crop index")
    for row in rows:
        if type(row["index"]) is not int:
            raise ValueError("Invalid index")
        for field in ("why","risk"):
            text=row[field]
            if not isinstance(text,str) or not text.strip() or len(text)>240 or '\n' in text:
                raise ValueError("Invalid explanation text")
            if len(re.split(r'[.!?]\s+(?=[A-Z])',text.strip()))>1:
                raise ValueError("Expected one sentence")
    return sorted(rows,key=lambda r:r["index"])


def explain(result, *, api_key=None, model=None, cache_dir=CACHE_DIR):
    api_key=os.getenv("OPENAI_API_KEY","") if api_key is None else api_key
    model=os.getenv("OPENAI_MODEL","") if model is None else model
    output={"entries":_rules(result),"source":"rule-based","disclaimer":DISCLAIMER,
            "notice":"Provisional screening; explanations do not change the scores."}
    if not result["top_three"] or not api_key.strip() or not model.strip():
        output["notice"] += " Configure OPENAI_API_KEY and OPENAI_MODEL to enable model wording."
        return output
    numeric=numeric_payload(result)
    request_text=json.dumps(numeric,allow_nan=False,sort_keys=True)
    digest=hashlib.sha256(("v1"+PROMPT+model+request_text).encode()).hexdigest()
    path=Path(cache_dir)/f"explanation_{digest}.json"
    try:
        rows=_validated(json.loads(path.read_text()),len(result["top_three"]))
        source="cached OpenAI"
    except (OSError,ValueError,KeyError,TypeError):
        client=None
        try:
            client=OpenAI(api_key=api_key,timeout=20,max_retries=1)
            schema={"type":"object","properties":{"crops":{"type":"array","items":{
                "type":"object","properties":{"index":{"type":"integer"},"why":{"type":"string"},"risk":{"type":"string"}},
                "required":["index","why","risk"],"additionalProperties":False}}},
                "required":["crops"],"additionalProperties":False}
            response=client.responses.create(model=model,instructions=PROMPT,input=request_text,store=False,
                max_output_tokens=1200,text={"format":{"type":"json_schema","name":"crop_explanations","strict":True,"schema":schema}})
            if response.status != "completed":
                raise ValueError("Incomplete model response")
            parsed=json.loads(response.output_text)
            rows=_validated(parsed,len(result["top_three"]))
            source="OpenAI"
            temp_path=None
            try:
                path.parent.mkdir(parents=True,exist_ok=True)
                with tempfile.NamedTemporaryFile(mode="w",dir=path.parent,delete=False,suffix=".tmp") as handle:
                    temp_path=Path(handle.name)
                    json.dump(parsed,handle)
                temp_path.replace(path)
            except OSError:
                pass
            finally:
                if temp_path:
                    try: temp_path.unlink(missing_ok=True)
                    except OSError: pass
        except (OpenAIError,ValueError,TypeError,KeyError,AttributeError):
            output["notice"] += " Model explanation unavailable; using the rule-based explanation."
            return output
        finally:
            if client is not None:
                client.close()
    for index,row in enumerate(rows):
        # Low matches retain deterministic wording even if model prose is overconfident.
        if result["top_three"][index]["strong_match"]:
            output["entries"][index].update(why=row["why"],risk=row["risk"])
    output["source"]=source
    return output
