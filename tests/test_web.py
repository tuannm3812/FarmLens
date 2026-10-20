import pytest
from farmlens.web import dispatch, validate_scenario, same_origin


def test_valid_scenario_keeps_precise_point():
    got=validate_scenario({'lat':-32.2569,'lon':148.6011,'mode':'season','month':5})
    assert got['lat']==-32.2569 and got['month']==5


@pytest.mark.parametrize('change',[{'lat':float('nan')},{'lat':True},{'lon':200},{'lat':-35.28,'lon':149.13},
                                  {'mode':'evil'},{'mode':'season','month':13},{'cache_only':'false'},{'refresh':1},
                                  {'irrigation':'yes'},{'category':'trees'}])
def test_bad_api_input_rejected(change):
    with pytest.raises(ValueError):validate_scenario({'lat':-32.2569,'lon':148.6011,**change})


def test_offline_api_returns_abstention_with_provenance(tmp_path):
    result=dispatch('/api/analyze',{'lat':-32.2569,'lon':148.6011,'cache_only':True},tmp_path)
    assert result['result']['top_three']==[]
    assert result['data']['soil']['data']['ph'] is None
    assert result['data']['soil']['status']=='offline'
    assert result['weights']['texture']==.15


def test_no_arbitrary_endpoint(tmp_path):
    with pytest.raises(ValueError):dispatch('/api/anything',{},tmp_path)


def test_imagery_route_is_independent_and_missing_metadata_stays_unknown(tmp_path):
    result = dispatch("/api/imagery", {
        "lat": -32.2569, "lon": 148.6011, "cache_only": True,
    }, tmp_path)
    assert result["status"] == "offline"
    assert result["data"]["blocks"] == []
    assert "result" not in result



def test_imagery_refresh_overrides_cache_only_and_saves_updated_metadata(tmp_path, fixture_json, monkeypatch):
    from datetime import datetime, timezone

    import requests
    from conftest import FakeSession
    from farmlens.imagery import ImageryClient

    point = {"lat": -32.2569, "lon": 148.6011, "cache_only": True}
    original = fixture_json("nsw_imagery_dates.json")
    ImageryClient(tmp_path, session=FakeSession(original)).fetch(point["lat"], point["lon"])
    updated = fixture_json("nsw_imagery_dates.json")
    # Synthetic newer survey date exercises cache replacement, not a source claim.
    updated["features"][0]["attributes"]["BlockStartDate"] = int(
        datetime(2021, 2, 1, tzinfo=timezone.utc).timestamp() * 1000
    )
    session = FakeSession(updated)
    monkeypatch.setattr(requests.Session, "get", lambda self, url, **kw: session.get(url, **kw))

    cached = dispatch("/api/imagery", point, tmp_path)
    assert cached["status"] == "cached"
    assert cached["data"]["blocks"][0]["survey_date"] == "2009-04-03"
    assert session.calls == []

    refreshed = dispatch("/api/imagery", {**point, "refresh": True}, tmp_path)
    assert refreshed["status"] == "live"
    assert refreshed["data"]["blocks"][0]["survey_date"] == "2021-02-01"
    assert len(session.calls) == 1

    saved = dispatch("/api/imagery", point, tmp_path)
    assert saved["status"] == "cached"
    assert saved["data"] == refreshed["data"]
    assert len(session.calls) == 1


def test_explain_rejects_changed_or_missing_shortlist(tmp_path):
    with pytest.raises(ValueError, match="changed"):
        dispatch('/api/explain',{'lat':-32.2569,'lon':148.6011,'cache_only':True,'fingerprint':'old'},tmp_path)


def test_local_origin_only():
    assert same_origin('http://127.0.0.1:8503','127.0.0.1:8503',8503)
    assert not same_origin('https://evil.example','127.0.0.1:8503',8503)
    assert not same_origin(None,'evil.example',8503)


def test_drainage_is_validated_and_propagated(tmp_path):
    with pytest.raises(ValueError):validate_scenario({'lat':-32.2569,'lon':148.6011,'drainage':'invented'})
    result=dispatch('/api/analyze',{'lat':-32.2569,'lon':148.6011,'cache_only':True,'drainage':'poorly_drained'},tmp_path)
    assert result['result']['drainage']=='poorly_drained'


def test_handler_returns_actionable_shortlist_mismatch_without_internal_errors(tmp_path,monkeypatch):
    import io,json
    from types import SimpleNamespace
    from farmlens.web import Handler
    payload=json.dumps({'lat':-32.2569,'lon':148.6011,'cache_only':True,'fingerprint':'old'}).encode()
    class Request:
        path='/api/explain'
        headers={'Host':'127.0.0.1:8503','Origin':'http://127.0.0.1:8503','Content-Type':'application/json','Content-Length':str(len(payload))}
        server=SimpleNamespace(server_port=8503)
        connection=SimpleNamespace(settimeout=lambda _:None)
        rfile=io.BytesIO(payload)
        def send(self,code,body):self.response=(code,body)
    monkeypatch.setenv('FARMLENS_CACHE_DIR',str(tmp_path))
    req=Request(); Handler.do_POST(req)
    assert req.response[0]==400
    assert 'shortlist changed' in req.response[1]['error'].lower()
    assert 'refresh' in req.response[1]['error'].lower()


def test_explain_rejects_fresh_to_stale_evidence_with_identical_scores(tmp_path, monkeypatch):
    from farmlens.api import DataResult
    import farmlens.web as web
    climate = DataResult({'annual_temperature_c':20,'annual_rainfall_mm':1400,
                          'coldest_month_min_c':10}, 'cached', 'climate')
    soil = DataResult({'ph':6.5,'clay_pct':20,'sand_pct':60,'soc_g_kg':20}, 'cached', 'soil')
    monkeypatch.setattr(web, 'load_point', lambda *a, **kw: {'climate':climate,'soil':soil})
    monkeypatch.setattr(web.FireClient, 'fetch', lambda *a, **kw: DataResult({'exposure':None},'offline','fire'))
    point = {'lat':-32.2569,'lon':148.6011,'cache_only':True}
    before = dispatch('/api/analyze', point, tmp_path)
    from dataclasses import replace
    soil = replace(soil, stale=True)
    after = dispatch('/api/analyze', point, tmp_path)
    assert before['result']['top_three'] == after['result']['top_three']
    with pytest.raises(ValueError, match='refresh'):
        dispatch('/api/explain', {**point,'fingerprint':before['fingerprint']}, tmp_path)


def test_explain_accepts_same_stale_evidence_after_failed_refresh(tmp_path, fixture_json, monkeypatch):
    """Cache retrieval wording must not masquerade as a changed crop report."""
    import json
    from datetime import date
    import requests
    from conftest import FakeSession
    from farmlens.api import DataResult
    from farmlens.climate import ClimateClient
    import farmlens.web as web

    point = {'lat':-32.2569, 'lon':148.6011}
    today = date(2026,10,20)
    ClimateClient(tmp_path, today=today, session=FakeSession(fixture_json('history.json'))).history(**point)
    path = next(tmp_path.glob('*.json'))
    envelope = json.loads(path.read_text())
    envelope['fetched_at'] = '2020-01-01T00:00:00+00:00'
    path.write_text(json.dumps(envelope))
    soil = DataResult({'ph':6.5,'clay_pct':20,'sand_pct':60,'soc_g_kg':20},'cached','soil')

    def load(lat, lon, **kwargs):
        client = ClimateClient(tmp_path, today=today, cache_only=kwargs['cache_only'],
                               session=FakeSession(requests.Timeout(), requests.Timeout()))
        return {'climate':client.history(lat,lon),'soil':soil}

    monkeypatch.setattr(web,'load_point',load)
    monkeypatch.setattr(web.FireClient,'fetch',lambda *a,**kw:DataResult({'exposure':None},'offline','fire'))
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    before = dispatch('/api/analyze', point, tmp_path)
    after = dispatch('/api/analyze', {**point,'cache_only':True}, tmp_path)
    assert before['data']['climate']['warning'] != after['data']['climate']['warning']
    assert before['result']['top_three'] == after['result']['top_three']
    assert before['fingerprint'] == after['fingerprint']
    explained = dispatch('/api/explain', {
        **point,'cache_only':True,'fingerprint':before['fingerprint'],
    }, tmp_path)
    assert explained['result']['top_three'] == before['result']['top_three']


@pytest.mark.parametrize('path,mime',[('/fonts/inter-latin.woff2','font/woff2'),('/fonts/manrope-latin.woff2','font/woff2'),('/comparison.js','text/javascript')])
def test_only_bundled_assets_are_served(path,mime):
    from types import SimpleNamespace
    from farmlens.web import Handler
    class Request:
        headers={'Host':'127.0.0.1:8503'}
        server=SimpleNamespace(server_port=8503)
        def send(self,*args):self.response=args
    req=Request();req.path=path;Handler.do_GET(req)
    assert req.response[0]==200
    assert req.response[2].startswith(mime)
    assert isinstance(req.response[1],bytes)
    req.path='/fonts/../../.env';Handler.do_GET(req)
    assert req.response[0]==404


@pytest.mark.parametrize('path,mime',[
    ('/assets/crops/canola.jpg','image/jpeg'),
    ('/assets/crops/manifest.json','application/json'),
    ('/assets/icons/crops.svg','image/svg+xml'),
    ('/assets/brand/finn.svg','image/svg+xml'),
    ('/assets/brand/wordmark.svg','image/svg+xml'),
    ('/assets/brand/mark-mono.svg','image/svg+xml'),
    ('/presentation.js','text/javascript'),
])
def test_crop_assets_have_explicit_safe_routes(path,mime):
    from types import SimpleNamespace
    from farmlens.web import Handler
    class Request:
        headers={'Host':'127.0.0.1:8503'}
        server=SimpleNamespace(server_port=8503)
        def send(self,*args):self.response=args
    req=Request();req.path=path;Handler.do_GET(req)
    assert req.response[0] == 200
    assert req.response[2].split(';')[0] == mime
    for denied in ['/assets/crops/../../.env','/assets/crops/%2e%2e/.env','/assets/crops/unlisted.jpg','/assets/README.md']:
        req.path=denied;Handler.do_GET(req)
        assert req.response[0] == 404


def test_water_api_is_isolated_from_scoring_and_omits_raw_daily_history(tmp_path, fixture_json, monkeypatch):
    from datetime import date, datetime
    from conftest import FakeSession
    from farmlens.water_climate import WaterClimateClient
    import farmlens.web as web
    class FixedClock:
        @classmethod
        def now(cls,tz):
            return datetime(2026,10,20,12,tzinfo=tz)
    monkeypatch.setattr(web,'datetime',FixedClock)
    WaterClimateClient(tmp_path,session=FakeSession(fixture_json('water_history.json')),today=date(2026,10,20)).history(-32.2569,148.6011)
    def unexpected(*args,**kwargs):
        raise AssertionError('Water must not load score sources or recommend crops')
    monkeypatch.setattr(web,'load_point',unexpected)
    monkeypatch.setattr(web,'recommend',unexpected)
    got = dispatch('/api/water',{'lat':-32.2569,'lon':148.6011,'cache_only':True,'crop_id':'barley'},tmp_path)
    assert got['assessment']['status'] == 'available'
    assert got['assessment']['profile']['name'] == 'Barley'
    assert got['source']['status'] == 'cached'
    assert 'data' not in got['source'] and 'dates' not in got['source']
    assert 'result' not in got and 'fingerprint' not in got


def test_water_api_validates_before_network_and_offline_abstains(tmp_path):
    point = {'lat':-32.2569,'lon':148.6011}
    with pytest.raises(ValueError,match='Starting water'):
        dispatch('/api/water',{**point,'soil_buffer_mm':10,'starting_water_mm':20},tmp_path)
    got = dispatch('/api/water',{**point,'cache_only':True},tmp_path)
    assert got['assessment']['status'] == 'unavailable'
    assert got['assessment']['summary'] is None
    assert got['source']['status'] == 'offline'


def test_reverse_api_keeps_label_separate_from_land_analysis(tmp_path,fixture_json,monkeypatch):
    from conftest import FakeSession
    from farmlens.geocode import Geocoder
    import farmlens.web as web
    monkeypatch.setattr('farmlens.geocode._rate_limit',lambda **kwargs:None)
    Geocoder(tmp_path,session=FakeSession(fixture_json('reverse_geocode.json'))).reverse(-32.2569,148.6011)
    def unexpected(*args,**kwargs):raise AssertionError('Name lookup must not run crop analysis')
    monkeypatch.setattr(web,'load_point',unexpected)
    got=dispatch('/api/reverse',{'lat':-32.2569,'lon':148.6011,'cache_only':True},tmp_path)
    assert got['data']=={'name':'Dubbo, NSW','kind':'locality'}
    assert got['status']=='cached'
    with pytest.raises(ValueError):dispatch('/api/reverse',{'lat':-35.28,'lon':149.13},tmp_path)


def test_land_cover_endpoint_is_independent_and_honest_offline(tmp_path,monkeypatch):
    import farmlens.web as web
    def unexpected(*a,**kw):raise AssertionError('Land cover must not invoke scoring')
    monkeypatch.setattr(web,'load_point',unexpected)
    got=dispatch('/api/land-cover',{'lat':-32.2569,'lon':148.6011,'cache_only':True},tmp_path)
    assert got['status']=='offline' and got['data']['class_code'] is None
    assert 'result' not in got
    with pytest.raises(ValueError):dispatch('/api/land-cover',{'lat':-35.28,'lon':149.13},tmp_path)


def test_budget_endpoint_isolated_and_unknown_inputs_remain_unknown(tmp_path,monkeypatch):
    monkeypatch.setattr('farmlens.web.load_point',lambda *a,**kw:pytest.fail('Budget must not load or change crop evidence'))
    point={'lat':-32.2569,'lon':148.6011}
    got=dispatch('/api/budget',{**point,'rows':[{'crop_id':'wheat'}]},tmp_path)
    assert got['rows'][0]['status']=='incomplete'
    with pytest.raises(ValueError):dispatch('/api/budget',{**point,'rows':[{'crop_id':'rice'}]},tmp_path)


def test_vegetation_endpoint_offline_never_substitutes_a_regional_estimate(tmp_path,monkeypatch):
    monkeypatch.setattr('farmlens.web.load_point',lambda *a,**kw:pytest.fail('Vegetation is independent'))
    got=dispatch('/api/vegetation',{'lat':-32.2569,'lon':148.6011,'cache_only':True},tmp_path)
    assert got['status']=='offline' and got['data']['samples']==[]


@pytest.mark.parametrize('path,page,active',[('/', 'Find crops that fit', '/'),('/explore','Land report','/explore'),('/explore/','Land report','/explore'),('/about','How FarmLens works','/about'),('/about/','How FarmLens works','/about'),('/index.html','Land report','/explore')])
def test_page_routes_have_shared_accessible_navigation(path,page,active):
    from types import SimpleNamespace
    from html.parser import HTMLParser
    from farmlens.web import Handler
    class Request:
        headers={'Host':'127.0.0.1:8503'}
        server=SimpleNamespace(server_port=8503)
        def send(self,*args):self.response=args
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.current=[];self.links=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='a':
                self.links.append(attrs.get('href'))
                if attrs.get('aria-current')=='page':self.current.append(attrs['href'])
    req=Request();req.path=path;Handler.do_GET(req)
    assert req.response[0]==200
    html=req.response[1].decode();assert page in html
    parser=Links();parser.feed(html)
    assert parser.current==[active]
    assert {'/','/explore','/about'}<=set(parser.links)
    assert '{{' not in html
    if active!='/explore':assert '/app.js' not in html
    if active=='/':
        assert {'/explore#dubbo','/explore#coffs-harbour','/explore#broken-hill'}<=set(parser.links)
