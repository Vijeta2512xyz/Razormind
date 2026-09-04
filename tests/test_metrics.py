import pandas as pd
import pytest
from app.detection.metrics import compute_dimension_metrics, compute_global_metrics, compute_metrics
from app.simulator.generator import SimulationConfig, generate_transactions
from app.simulator.incidents import IncidentConfig, inject_incident


def _data():
    return generate_transactions(SimulationConfig(start="2026-01-01 12:00:00", minutes=30, seed=42, base_transactions_per_minute=100))


def test_global_metrics_schema_and_one_row_per_minute():
    metrics = compute_global_metrics(_data())
    expected = {"timestamp", "transaction_count", "success_count", "failure_count", "success_rate", "failure_rate", "mean_latency_ms", "p50_latency_ms", "p95_latency_ms", "timeout_count", "timeout_rate", "retry_count", "retry_rate"}
    assert expected.issubset(metrics.columns)
    assert len(metrics) == 30
    assert metrics["transaction_count"].min() > 0


def test_rates_bounded():
    metrics = compute_global_metrics(_data())
    for column in ["success_rate", "failure_rate", "timeout_rate", "retry_rate"]:
        assert metrics[column].between(0, 1).all()


def test_counts_reconcile():
    metrics = compute_global_metrics(_data())
    assert (metrics["success_count"] + metrics["failure_count"] == metrics["transaction_count"]).all()
    assert (metrics["timeout_count"] <= metrics["transaction_count"]).all()
    assert (metrics["retry_count"] <= metrics["transaction_count"]).all()


def test_p95_at_least_p50():
    metrics = compute_global_metrics(_data())
    assert (metrics["p95_latency_ms"] >= metrics["p50_latency_ms"]).all()


def test_bank_dimension():
    metrics = compute_dimension_metrics(_data(), "bank")
    assert set(metrics["bank"].unique()) == {"hdfc", "sbi", "icici", "axis", "kotak", "yes_bank"}
    assert len(metrics) == 30 * 6


def test_payment_method_dimension():
    metrics = compute_dimension_metrics(_data(), "payment_method")
    assert set(metrics["payment_method"].unique()) == {"upi", "card", "netbanking", "wallet"}


def test_metrics_reveal_injected_bank_incident():
    df = _data()
    incident = IncidentConfig(incident_id="INC-M3-001", incident_type="bank_failure", start_time="2026-01-01 12:10:00", end_time="2026-01-01 12:20:00", severity="high", affected_component="bank", affected_bank="hdfc", expected_symptoms=("bank_failure_rate_increase",))
    modified, _ = inject_incident(df, incident, seed=100)
    before = compute_dimension_metrics(df, "bank")
    after = compute_dimension_metrics(modified, "bank")
    mask = (before["timestamp"] >= pd.Timestamp("2026-01-01 12:10:00")) & (before["timestamp"] <= pd.Timestamp("2026-01-01 12:19:00")) & (before["bank"] == "hdfc")
    assert after.loc[mask, "failure_rate"].mean() > before.loc[mask, "failure_rate"].mean() + 0.20


def test_empty_input_returns_schema():
    empty = pd.DataFrame(columns=["timestamp", "status", "latency_ms", "http_status", "error_code", "retry_count"])
    metrics = compute_metrics(empty)
    assert "timestamp" in metrics.columns
    assert "success_rate" in metrics.columns
    assert metrics.empty


def test_invalid_dimension_rejected():
    with pytest.raises(ValueError, match="Unsupported dimensions"):
        compute_metrics(_data(), dimensions=["country"])
