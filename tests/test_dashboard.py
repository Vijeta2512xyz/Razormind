from pathlib import Path

import pandas as pd

from app.dashboard import build_dashboard_snapshot, load_runbooks


def sample_df():
    return pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=4, freq="min"),
        "status": ["success", "failed", "success", "success"],
        "latency_ms": [100.0, 200.0, 120.0, 150.0],
        "http_status": [200, 500, 200, 200],
        "error_code": ["", "GATEWAY_5XX", "", ""],
        "retry_count": [0, 1, 0, 0],
        "payment_method": ["upi"] * 4,
        "bank": ["hdfc"] * 4,
        "region": ["north"] * 4,
        "merchant": ["m1"] * 4,
    })


def test_dashboard_snapshot_contains_real_metrics():
    result = build_dashboard_snapshot(sample_df())
    assert len(result["metrics"]) == 4
    assert result["latest"]["transaction_count"] == 1


def test_dashboard_snapshot_has_reliability_columns():
    result = build_dashboard_snapshot(sample_df())
    for col in ("failure_rate", "timeout_rate", "retry_rate", "p95_latency_ms"):
        assert col in result["metrics"]


def test_runbooks_load_from_knowledge_base():
    retriever = load_runbooks()
    results = retriever.search("upi degradation", top_k=1)
    assert len(results) == 1
    assert results[0]["score"] > 0


def test_dashboard_module_has_default_database_path():
    from app import dashboard
    assert dashboard.DEFAULT_DB.name == "razormind.db"
