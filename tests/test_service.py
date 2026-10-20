from datetime import datetime, timezone

from farmlens.api import DataResult
from farmlens.service import needs_revalidation


def test_current_forecast_expires_within_same_calendar_day():
    data={"forecast":DataResult({},"cached","Open-Meteo", "2026-10-20T08:00:00+00:00")}
    assert not needs_revalidation(data,datetime(2026,10,20,11,59,tzinfo=timezone.utc))
    assert needs_revalidation(data,datetime(2026,10,20,12,tzinfo=timezone.utc))


def test_already_stale_and_offline_results_do_not_trigger_rerun_fetch_loops():
    data={"forecast":DataResult({},"cached","test","2026-10-20T08:00:00+00:00",True),
          "soil":DataResult({},"offline","test")}
    assert not needs_revalidation(data,datetime(2026,10,20,20,tzinfo=timezone.utc))
