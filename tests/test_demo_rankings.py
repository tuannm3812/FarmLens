from datetime import date

from scripts.demo_rankings import build_scenarios, render_markdown


def test_scenario_matrix_is_offline_and_abstains_without_seasonal_data(tmp_path):
    scenarios = build_scenarios(tmp_path, date(2026, 10, 20))
    assert len(scenarios) == 18
    assert {r["location"] for r in scenarios} == {"Coffs Harbour", "Dubbo", "Broken Hill"}
    assert {r["result"]["irrigation"] for r in scenarios} == {"rainfed", "irrigated"}
    assert all(r["result"]["sources"]["climate"]["status"] == "offline" for r in scenarios)
    assert all(r["result"]["top_three"] == [] for r in scenarios if r["result"]["mode"] == "season")
    text = render_markdown(scenarios, date(2026, 10, 20))
    assert "No eligible candidates" in text
    assert "offline" in text
    assert "Indicative only. Check with a local agronomist." in text
