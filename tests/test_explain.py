import json
from types import SimpleNamespace

import pytest

from farmlens.explain import explain, numeric_payload, DISCLAIMER
from farmlens.scoring import load_crops, score_crop


@pytest.fixture
def result():
    crop = score_crop(load_crops()[0], temperature_c=18, rainfall_mm=525, ph=6.5, frost_min_c=5)
    crop["inputs"] = {"temperature_c":18,"annual_rainfall_mm":525,"ph":6.5,"frost_min_c":5}
    return {"top_three":[crop],"mode":"explore","planting_month":None,"irrigation":"rainfed",
            "evidence_quality":"provisional — offline inputs", "location":"Private Farm, 123 Secret Road"}


def test_no_key_explains_strength_and_risk_and_disclaimer(result, tmp_path):
    output = explain(result, api_key="", model="", cache_dir=tmp_path)
    assert output["source"] == "rule-based"
    assert "rainfall" in output["entries"][0]["risk"].lower()
    assert output["disclaimer"] == DISCLAIMER


def test_payload_contains_only_numbers_and_no_personal_or_free_text(result):
    def walk(value):
        if isinstance(value, dict):
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
        else:
            assert value is None or type(value) in (int,float)
    payload=numeric_payload(result)
    walk(payload)
    assert "Private" not in json.dumps(payload)
    assert "wheat" not in json.dumps(payload)
    assert payload["offline_or_stale"] == 1


def test_model_response_is_validated_and_cached(result, tmp_path, fixture_json, monkeypatch):
    calls=[]
    class Client:
        def __init__(self, **kwargs):
            assert kwargs["timeout"] == 20
            assert kwargs["max_retries"] == 1
            self.responses=self
        def create(self, **kwargs):
            calls.append(kwargs)
            assert kwargs["store"] is False
            assert "Secret" not in kwargs["input"]
            return SimpleNamespace(output_text=json.dumps(fixture_json("explanation.json")), status="completed")
        def close(self): pass
    monkeypatch.setattr("farmlens.explain.OpenAI", Client)
    out=explain(result, api_key="test", model="configured-model", cache_dir=tmp_path)
    assert out["source"] == "OpenAI"
    assert out["entries"][0]["id"] == result["top_three"][0]["id"]
    again=explain(result, api_key="test", model="configured-model", cache_dir=tmp_path)
    assert again["source"] == "cached OpenAI"
    assert len(calls)==1


@pytest.mark.parametrize("response", ["not json", '{"crops":[]}', '{"crops":[{"index":0,"why":"","risk":"ok"}]}'])
def test_bad_model_response_falls_back_without_crashing(result,tmp_path,monkeypatch,response):
    class Client:
        def __init__(self,**kwargs): self.responses=self
        def create(self,**kwargs): return SimpleNamespace(output_text=response,status="completed")
        def close(self): pass
    monkeypatch.setattr("farmlens.explain.OpenAI",Client)
    assert explain(result,api_key="test",model="test",cache_dir=tmp_path)["source"] == "rule-based"


def test_timeout_falls_back_and_does_not_expose_secrets(result,tmp_path,monkeypatch):
    from openai import APITimeoutError
    import httpx
    class Client:
        def __init__(self,**kwargs): self.responses=self
        def create(self,**kwargs): raise APITimeoutError(request=httpx.Request("POST","https://example.com/secret"))
        def close(self): pass
    monkeypatch.setattr("farmlens.explain.OpenAI",Client)
    output=explain(result,api_key="test",model="test",cache_dir=tmp_path)
    assert output["source"] == "rule-based"
    assert "secret" not in json.dumps(output)


def test_failed_crop_is_not_described_as_suitable(result,tmp_path):
    result["top_three"][0].update(total=20,strong_match=False,zero_capped=True)
    result["top_three"][0]["subscores"]["rainfall"]=0
    out=explain(result,api_key="",model="",cache_dir=tmp_path)
    assert "not a strong match" in out["entries"][0]["why"]
    assert "absolute" in out["entries"][0]["risk"]


def test_local_guidance_cautions_survive_model_wording_and_stay_private(result,tmp_path,fixture_json,monkeypatch):
    result['top_three'][0]['guidance']={'checks':[{'status':'not_assessed','message':'Obtain a pHCa soil profile.'}]}
    class Client:
        def __init__(self,**kwargs): self.responses=self
        def create(self,**kwargs):
            assert 'pHCa soil profile' not in kwargs['input']
            return SimpleNamespace(output_text=json.dumps(fixture_json('explanation.json')),status='completed')
        def close(self):pass
    monkeypatch.setattr('farmlens.explain.OpenAI',Client)
    output=explain(result,api_key='test',model='test',cache_dir=tmp_path)
    assert output['entries'][0]['local_cautions']==['Obtain a pHCa soil profile.']
