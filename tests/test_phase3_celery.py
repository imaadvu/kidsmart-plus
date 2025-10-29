from core.etl import celery_app
from celery.schedules import crontab


def test_celery_beat_schedule_exists():
    assert celery_app is not None
    sched = celery_app.conf.beat_schedule
    assert isinstance(sched, dict)
    assert "nightly-ingest" in sched
    entry = sched["nightly-ingest"]
    assert entry.get("task") == "core.etl.run_ingest_task"
    assert isinstance(entry.get("schedule"), crontab)
