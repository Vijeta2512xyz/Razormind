import numpy as np
import pandas as pd

from app.detection.baseline import add_ewma_baseline, add_rolling_baseline
from app.detection.detector import detect_anomalies


def make_metrics(values=None):
    n = 30
    timestamps = pd.date_range("2026-01-01 10:00:00", periods=n, freq="min")
    failure = np.full(n, 0.02) if values is None else np.asarray(values, dtype=float)
    return pd.DataFrame({
        "timestamp": timestamps,
        "failure_rate": failure,
        "timeout_rate": np.full(n, 0.005),
        "p95_latency_ms": np.full(n, 250.0),
        "retry_rate": np.full(n, 0.02),
    })


def test_rolling_baseline_does_not_look_ahead():
    df = make_metrics([0.02] * 9 + [0.90] + [0.02] * 20)
    out = add_rolling_baseline(df, "failure_rate", window=5)
    assert out.loc[9, "failure_rate_baseline_mean"] == 0.02


def test_rolling_baseline_schema():
    out = add_rolling_baseline(make_metrics(), "failure_rate", window=5)
    assert {"failure_rate_baseline_mean", "failure_rate_baseline_std"}.issubset(out.columns)


def test_ewma_baseline_schema():
    out = add_ewma_baseline(make_metrics(), "failure_rate", span=5)
    assert "failure_rate_ewma" in out.columns
    assert pd.isna(out.loc[0, "failure_rate_ewma"])


def test_detector_flags_large_failure_rate_spike():
    values = [0.02] * 15 + [0.25] + [0.02] * 14
    out = detect_anomalies(make_metrics(values), value_columns=["failure_rate"], window=10)
    assert bool(out.loc[15, "is_anomaly"])
    assert "failure_rate" in out.loc[15, "anomaly_reasons"]


def test_detector_does_not_flag_stable_metrics():
    out = detect_anomalies(make_metrics(), window=10)
    assert not out["is_anomaly"].any()


def test_detector_supports_latency_spike():
    df = make_metrics()
    df.loc[20, "p95_latency_ms"] = 900.0
    out = detect_anomalies(df, value_columns=["p95_latency_ms"], window=10)
    assert bool(out.loc[20, "is_anomaly"])


def test_detector_returns_score_and_reason_columns():
    out = detect_anomalies(make_metrics(), window=10)
    assert out["anomaly_score"].dtype.kind in "fi"
    assert out["anomaly_reasons"].dtype == object


def test_invalid_value_column_rejected():
    try:
        detect_anomalies(make_metrics(), value_columns=["does_not_exist"])
    except ValueError as exc:
        assert "Missing metric columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_empty_input_is_supported():
    empty = make_metrics().iloc[0:0]
    out = detect_anomalies(empty)
    assert out.empty
    assert {"anomaly_score", "is_anomaly", "anomaly_reasons"}.issubset(out.columns)
