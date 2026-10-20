from datetime import date
from types import SimpleNamespace

import pytest
import requests

from farmlens.fire import FireClient, count_detections, csv_payload, date_windows


class FireSession:
    def __init__(self, fixture, fail=False):
        self.fixture=fixture
        self.fail=fail
        self.calls=[]
    def get(self,url,**kwargs):
        self.calls.append((url,kwargs))
        if self.fail:
            raise requests.Timeout("secret key in URL must never escape")
        text=self.fixture["availability"] if "data_availability" in url else self.fixture["detections"] if url.endswith("/2023-01-01") else self.fixture["empty"]
        return SimpleNamespace(text=text,raise_for_status=lambda:None)


def test_radius_date_and_duplicate_filtering(fixture_json):
    rows=csv_payload(SimpleNamespace(text=fixture_json("firms.json")["detections"]))
    assert count_detections(rows,-32.26,148.6,date(2023,1,1),date(2023,1,5))["count"]==2
    with pytest.raises(ValueError):
        count_detections(rows,-32.26,148.6,date(2024,1,1),date(2024,1,5))


def test_windows_cover_leap_year_without_overlaps():
    windows=list(date_windows(date(2023,1,1),date(2025,12,31)))
    assert len(windows)==220
    assert sum((b-a).days+1 for a,b in windows)==1096
    assert windows[-1][1]==date(2025,12,31)
    assert all((b-a).days < 5 for a,b in windows)


def test_missing_key_skips_all_network(tmp_path):
    result=FireClient(tmp_path,map_key="").fetch(-32.26,148.6)
    assert result.data["exposure"] is None
    assert result.data["note"] == "fire data not configured"


def test_full_history_counts_and_cached_retry_fallback(fixture_json,tmp_path):
    session=FireSession(fixture_json("firms.json"))
    client=FireClient(tmp_path,session=session,map_key="test",today=date(2026,10,20))
    result=client.fetch(-32.26,148.6)
    assert result.status=="live"
    assert result.data["count"]==2
    assert result.data["exposure"]=="low"
    assert result.data["period"]=="2023–2025"
    assert result.data["complete"] is True
    assert len(session.calls)==221
    assert all(kwargs["timeout"]==(5,20) for _,kwargs in session.calls)
    client.session=FireSession(fixture_json("firms.json"),fail=True)
    cached=client.fetch(-32.26,148.6,refresh=True)
    assert cached.status=="cached"
    assert cached.data["count"]==2
    assert "secret" not in cached.warning


def test_incomplete_history_never_becomes_low_exposure(fixture_json,tmp_path):
    session=FireSession(fixture_json("firms.json"),fail=True)
    result=FireClient(tmp_path,session=session,map_key="test",today=date(2026,10,20)).fetch(-32.26,148.6)
    assert result.status=="offline"
    assert result.data["count"] is None
    assert result.data["exposure"] is None
    assert len(session.calls)==2


def test_availability_gap_prevents_area_calls(fixture_json,tmp_path):
    fixture=fixture_json("firms.json")
    fixture["availability"]="data_id,min_date,max_date\nVIIRS_SNPP_SP,2012-01-20,2025-06-30\n"
    session=FireSession(fixture)
    result=FireClient(tmp_path,session=session,map_key="test",today=date(2026,10,20)).fetch(-32.26,148.6)
    assert result.data["exposure"] is None
    assert len(session.calls)==1


def test_html_error_or_missing_headers_is_not_zero_detections():
    for body in ("<html>Invalid MAP_KEY</html>","", "error,message\nerror,invalid\n"):
        with pytest.raises(ValueError):
            count_detections(csv_payload(SimpleNamespace(text=body)),-32.26,148.6,date(2023,1,1),date(2023,1,5))


def test_fire_budget_limits_request_timeouts_and_stops_retry(fixture_json,tmp_path,monkeypatch):
    clock=[0.0]
    monkeypatch.setattr("farmlens.fire.time.monotonic",lambda:clock[0])
    class SlowSession(FireSession):
        def get(self,url,**kwargs):
            if "data_availability" in url:
                clock[0]+=19
                return super().get(url,**kwargs)
            self.calls.append((url,kwargs))
            clock[0]+=sum(kwargs["timeout"])
            raise requests.Timeout()
    session=SlowSession(fixture_json("firms.json"))
    result=FireClient(tmp_path,session=session,map_key="test",today=date(2026,10,20)).fetch(-32.26,148.6,max_seconds=20)
    assert clock[0] <= 20
    assert len(session.calls)==2
    assert result.data["exposure"] is None
