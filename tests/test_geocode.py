import requests
import pytest

from conftest import FakeSession
from farmlens.geocode import Geocoder
from farmlens.geocode import _rate_limit as real_rate_limit


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr("farmlens.geocode._rate_limit",lambda **kwargs:None)


def test_geocode_fixture_filters_nsw_and_caches(fixture_json,tmp_path):
    session=FakeSession(fixture_json("geocode.json"))
    client=Geocoder(tmp_path,session=session)
    result=client.search("Dubbo")
    assert result.status=="live"
    assert len(result.data["matches"])==2
    assert result.data["matches"][0]["lat"] == -32.2569
    assert session.calls[0][1]["params"]["countrycodes"]=="au"
    assert session.calls[0][1]["headers"]["User-Agent"].startswith("FarmLens")
    assert client.search("  DUBBO ").status=="cached"
    assert len(session.calls)==1


def test_geocoder_fails_without_inventing_location(tmp_path):
    session=FakeSession(requests.Timeout(),requests.Timeout())
    result=Geocoder(tmp_path,session=session).search("Unknown farm")
    assert result.status=="offline"
    assert result.data["matches"]==[]
    assert "regional" not in result.warning.lower()
    assert len(session.calls)==2


def test_empty_geocode_is_valid_no_result(tmp_path):
    result=Geocoder(tmp_path,session=FakeSession([])).search("Not a place")
    assert result.status=="live"
    assert result.data["matches"]==[]


def test_failed_refresh_uses_real_cached_search(fixture_json,tmp_path):
    client=Geocoder(tmp_path,session=FakeSession(fixture_json("geocode.json")))
    client.search("Dubbo")
    client.session=FakeSession(requests.Timeout(),requests.Timeout())
    result=client.search("Dubbo",refresh=True)
    assert result.status=="cached"
    assert len(result.data["matches"])==2


def test_invalid_payload_is_not_a_live_no_result(tmp_path):
    result=Geocoder(tmp_path,session=FakeSession({},{})).search("Dubbo")
    assert result.status=="offline"


def test_reverse_locality_uses_rounded_point_and_cached_label(fixture_json,tmp_path):
    session=FakeSession(fixture_json('reverse_geocode.json'))
    client=Geocoder(tmp_path,session=session)
    result=client.reverse(-32.2569,148.6011)
    assert result.status=='live'
    assert result.data=={'name':'Dubbo, NSW','kind':'locality'}
    assert session.calls[0][1]['params']=={
        'lat':-32.26,'lon':148.6,'format':'jsonv2','addressdetails':1,'zoom':12,'accept-language':'en'}
    assert session.calls[0][0].endswith('/reverse')
    assert session.calls[0][1]['timeout']
    assert session.calls[0][1]['headers']['User-Agent'].startswith('FarmLens')
    assert client.reverse(-32.257,148.601).status=='cached'
    assert len(session.calls)==1


def test_reverse_failure_retains_cached_name_or_returns_unknown(fixture_json,tmp_path):
    client=Geocoder(tmp_path,session=FakeSession(fixture_json('reverse_geocode.json')))
    client.reverse(-32.2569,148.6011)
    client.session=FakeSession(requests.Timeout(),requests.Timeout())
    saved=client.reverse(-32.2569,148.6011,refresh=True)
    assert saved.status=='cached' and saved.data['name']=='Dubbo, NSW'
    offline=Geocoder(tmp_path,cache_only=True).reverse(-31.95,141.45)
    assert offline.status=='offline' and offline.data['name'] is None


@pytest.mark.parametrize('address,expected',[
    ({'suburb':'North Dubbo','city':'Dubbo'},'North Dubbo, NSW'),
    ({'county':'Central Darling Shire Council'},'Central Darling Shire Council, NSW'),
    ({'road':'Private Farm Road','house_number':'7'},None),
    ({'state':'Victoria','ISO3166-2-lvl4':'AU-VIC','city':'Wodonga'},None),
    ({'country_code':'nz','city':'Dubbo'},None),
])
def test_reverse_does_not_invent_a_property_name(fixture_json,tmp_path,address,expected):
    payload=fixture_json('reverse_geocode.json')
    payload['address']={'state':'New South Wales','ISO3166-2-lvl4':'AU-NSW','country_code':'au',**address}
    got=Geocoder(tmp_path,session=FakeSession(payload)).reverse(-32.2569,148.6011)
    assert got.data['name']==expected


def test_reverse_invalid_points_rejected_before_network(tmp_path):
    client=Geocoder(tmp_path)
    for lat,lon in [(True,148.6),(-35.28,149.13),(float('nan'),148.6)]:
        with pytest.raises(ValueError):client.reverse(lat,lon)


def test_reverse_empty_coverage_and_invalid_response(tmp_path):
    empty=Geocoder(tmp_path,session=FakeSession({'error':'Unable to geocode'})).reverse(-32.2569,148.6011)
    assert empty.status=='live' and empty.data['name'] is None
    malformed=Geocoder(tmp_path,session=FakeSession([],[])).reverse(-31.95,141.45)
    assert malformed.status=='offline' and malformed.data['name'] is None


def test_reverse_rate_limit_respects_deadline_when_another_request_holds_lock(monkeypatch):
    import threading,time
    lock=threading.Lock();lock.acquire()
    monkeypatch.setattr('farmlens.geocode._lock',lock)
    # Release eventually so a broken unbounded acquisition cannot hang the suite.
    release=threading.Timer(.2,lock.release);release.start()
    try:
        with pytest.raises(requests.Timeout):real_rate_limit(deadline=time.monotonic()+.02)
    finally:release.join()


def test_reverse_rate_limit_does_not_sleep_past_deadline(monkeypatch):
    import threading,time
    monkeypatch.setattr('farmlens.geocode._lock',threading.Lock())
    monkeypatch.setattr('farmlens.geocode._last_request',time.monotonic())
    with pytest.raises(requests.Timeout):real_rate_limit(deadline=time.monotonic()+.02)
