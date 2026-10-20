from streamlit.testing.v1 import AppTest
from farmlens.config import ROOT


def run_app(monkeypatch, tmp_path):
    monkeypatch.setenv("FARMLENS_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FIRMS_MAP_KEY", raising=False)
    monkeypatch.setattr("streamlit_folium.st_folium", lambda *a, **kw: {})
    return AppTest.from_file(ROOT / "app.py", default_timeout=10).run()


def test_app_cached_soil_explanation_and_preset_abstention(monkeypatch, tmp_path, fixture_json):
    from conftest import FakeSession
    from farmlens.australian_soil import AustralianSoilClient
    from farmlens.config import PRESETS
    for code in ("PHW", "CLY", "SND", "SOC"):
        client = AustralianSoilClient(tmp_path, session=FakeSession(fixture_json(f"slga_{code.lower()}.json")))
        client.fetch_property(code, *PRESETS["Dubbo"])
    app = run_app(monkeypatch, tmp_path)
    assert not app.exception
    assert any("offline data" in w.value.lower() for w in app.warning)
    assert len(app.get("progress")) == 18
    app.button(key="explain").click().run()
    assert app.session_state["explanation"]["source"] == "rule-based"
    app.selectbox(key="preset").select("Broken Hill").run()
    assert not app.exception
    assert app.session_state["location"]["name"] == "Broken Hill"
    assert "explanation" not in app.session_state
    app.radio(key="mode").set_value("Plan next season").run()
    assert not app.exception
    assert any("monthly climate" in w.value.lower() for w in app.warning)
    assert app.button(key="explain").disabled


def test_no_soil_cache_disables_recommendations(monkeypatch, tmp_path):
    app = run_app(monkeypatch, tmp_path)
    assert not app.exception
    assert app.button(key="explain").disabled
    assert not app.get("progress")
    assert any("Soil pH" in w.value for w in app.warning)
    assert not any("No strong match" in w.value for w in app.warning)


def test_no_strong_match_is_visible_for_low_rainfall(monkeypatch, tmp_path):
    from farmlens.api import DataResult
    def point(*a, **kw):
        return {
            "climate": DataResult({"annual_rainfall_mm":100,"annual_temperature_c":18,"coldest_month_min_c":5,
                                   "driest_three_months_mm":20,"period":"2016–2025"},"cached","test"),
            "soil": DataResult({"ph":6.5,"clay_pct":30,"sand_pct":40,"soc_g_kg":12,"texture":"medium textured"},"offline","test"),
            "forecast": DataResult({"note":"Outlook unavailable","start_date":None,"end_date":None},"offline","test"),
        }
    monkeypatch.setattr("farmlens.service.load_point", point)
    app=run_app(monkeypatch, tmp_path)
    assert not app.exception
    assert any("No strong match" in w.value for w in app.warning)


def test_drainage_change_invalidates_explanation_and_resets_for_new_location(monkeypatch, tmp_path, fixture_json):
    from conftest import FakeSession
    from farmlens.australian_soil import AustralianSoilClient
    from farmlens.config import PRESETS
    for code in ("PHW", "CLY", "SND", "SOC"):
        client = AustralianSoilClient(tmp_path, session=FakeSession(fixture_json(f"slga_{code.lower()}.json")))
        client.fetch_property(code, *PRESETS["Dubbo"])
    app = run_app(monkeypatch, tmp_path)
    assert not app.exception
    assert any("Local checks required" in caption.value for caption in app.caption)
    assert any("Brassica napus species profile" in element.value for element in app.markdown)
    assert any("**Not assessed**" in element.value for element in app.markdown)
    assert any(expander.label == "Local checks & sources" for expander in app.expander)
    app.button(key="explain").click().run()
    assert "explanation" in app.session_state
    app.selectbox(key="drainage").select("well_drained").run()
    assert not app.exception
    assert "explanation" not in app.session_state
    app.selectbox(key="preset").select("Broken Hill").run()
    assert not app.exception
    assert app.selectbox(key="drainage").value == "unknown"
