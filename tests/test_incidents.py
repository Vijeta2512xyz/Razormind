import pandas as pd
import pytest

from app.simulator.generator import SimulationConfig, generate_transactions
from app.simulator.incidents import IncidentConfig, inject_incident


def _base_df():
    return generate_transactions(
        SimulationConfig(
            start="2026-01-01 12:00:00", minutes=60, seed=42, base_transactions_per_minute=100
        )
    )


def _incident(incident_type, **kwargs):
    defaults = dict(
        incident_id="INC-001",
        incident_type=incident_type,
        start_time="2026-01-01 12:20:00",
        end_time="2026-01-01 12:40:00",
        severity="high",
        affected_component=incident_type,
        expected_symptoms=("failure_rate_increase",),
    )
    defaults.update(kwargs)
    return IncidentConfig(**defaults)


def _window(df):
    return pd.to_datetime(df["timestamp"]).between(
        "2026-01-01 12:20:00", "2026-01-01 12:40:00"
    )


def test_upi_degradation_is_concentrated_on_upi():
    df = _base_df()
    modified, _ = inject_incident(df, _incident(
        "upi_degradation", affected_component="upi", affected_payment_method="upi"
    ), seed=10)
    w = _window(df)
    before, after = df[w], modified[w]
    upi_before = before[before.payment_method == "upi"].status.eq("failed").mean()
    upi_after = after[after.payment_method == "upi"].status.eq("failed").mean()
    card_before = before[before.payment_method == "card"].status.eq("failed").mean()
    card_after = after[after.payment_method == "card"].status.eq("failed").mean()
    assert upi_after > upi_before + 0.20
    assert card_after - card_before < 0.10


def test_bank_failure_targets_only_selected_bank():
    df = _base_df()
    modified, _ = inject_incident(df, _incident(
        "bank_failure", affected_component="bank", affected_bank="hdfc"
    ), seed=11)
    w = _window(df)
    before, after = df[w], modified[w]
    hdfc_before = before[before.bank == "hdfc"].status.eq("failed").mean()
    hdfc_after = after[after.bank == "hdfc"].status.eq("failed").mean()
    other_before = before[before.bank != "hdfc"].status.eq("failed").mean()
    other_after = after[after.bank != "hdfc"].status.eq("failed").mean()
    assert hdfc_after > hdfc_before + 0.25
    assert other_after - other_before < 0.10


def test_latency_spike_materially_increases_latency():
    df = _base_df()
    modified, _ = inject_incident(df, _incident("latency_spike", affected_component="gateway"), seed=12)
    w = _window(df)
    assert modified.loc[w, "latency_ms"].mean() > df.loc[w, "latency_ms"].mean() * 1.8


def test_gateway_failure_increases_gateway_errors():
    df = _base_df()
    modified, _ = inject_incident(df, _incident("gateway_failure", affected_component="payment_gateway"), seed=13)
    w = _window(df)
    gateway_errors = modified.loc[w, "error_code"].isin(["GATEWAY_ERROR", "UPSTREAM_5XX"])
    assert gateway_errors.mean() > 0.30


def test_timeout_spike_increases_timeout_rate_and_retries():
    df = _base_df()
    modified, _ = inject_incident(df, _incident("timeout_spike", affected_component="payment_gateway"), seed=14)
    w = _window(df)
    assert modified.loc[w, "error_code"].eq("TIMEOUT").mean() > 0.25
    assert modified.loc[w, "retry_count"].mean() > df.loc[w, "retry_count"].mean()


def test_regional_degradation_targets_selected_region():
    df = _base_df()
    modified, _ = inject_incident(df, _incident(
        "regional_degradation", affected_component="region", affected_region="north"
    ), seed=15)
    w = _window(df)
    before, after = df[w], modified[w]
    north_before = before[before.region == "north"].status.eq("failed").mean()
    north_after = after[after.region == "north"].status.eq("failed").mean()
    other_before = before[before.region != "north"].status.eq("failed").mean()
    other_after = after[after.region != "north"].status.eq("failed").mean()
    assert north_after > north_before + 0.20
    assert other_after - other_before < 0.10


def test_required_target_is_validated():
    df = _base_df()
    with pytest.raises(ValueError, match="affected_bank"):
        inject_incident(df, _incident("bank_failure"))
