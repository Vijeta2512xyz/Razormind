import pandas as pd

from app.diagnosis.evidence import extract_incident_evidence
from app.diagnosis.root_cause import diagnose_incident
from app.simulator.generator import SimulationConfig, generate_transactions
from app.simulator.incidents import IncidentConfig, inject_incident


def base_data():
    return generate_transactions(SimulationConfig(minutes=120, seed=42, base_transactions_per_minute=60))


def incident():
    return IncidentConfig(
        incident_id="INC-005",
        incident_type="bank_failure",
        start_time="2026-01-01T00:30:00",
        end_time="2026-01-01T00:45:00",
        severity="high",
        affected_component="bank:hdfc",
        affected_bank="hdfc",
        expected_symptoms=("failure_rate_increase", "latency_increase"),
    )


def test_evidence_contains_core_metrics():
    df, _ = inject_incident(base_data(), incident(), seed=7)
    evidence = extract_incident_evidence(df, incident().start_time, incident().end_time)
    assert evidence["transaction_count"] > 0
    assert 0 <= evidence["failure_rate"] <= 1
    assert "by_bank" in evidence
    assert "error_counts" in evidence


def test_evidence_rejects_non_overlapping_window():
    df = base_data()
    try:
        extract_incident_evidence(df, "2027-01-01", "2027-01-01T01:00:00")
    except ValueError as exc:
        assert "does not overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_bank_failure_ranks_affected_bank():
    inc = incident()
    df, _ = inject_incident(base_data(), inc, seed=7)
    result = diagnose_incident(df, inc)
    assert result["leading_hypothesis"]["component"] == "bank:hdfc"


def test_diagnosis_returns_ranked_hypotheses():
    inc = incident()
    df, _ = inject_incident(base_data(), inc, seed=7)
    result = diagnose_incident(df, inc)
    assert result["ranked_hypotheses"]
    scores = [h["score"] for h in result["ranked_hypotheses"]]
    assert scores == sorted(scores, reverse=True)


def test_ground_truth_is_preserved():
    inc = incident()
    df, _ = inject_incident(base_data(), inc, seed=7)
    result = diagnose_incident(df, inc)
    assert result["ground_truth"]["incident_id"] == "INC-005"
    assert result["expected_component"] == "bank:hdfc"


def test_latency_spike_produces_latency_evidence():
    inc = IncidentConfig(
        incident_id="INC-LAT",
        incident_type="latency_spike",
        start_time="2026-01-01T00:30:00",
        end_time="2026-01-01T00:45:00",
        severity="medium",
        affected_component="gateway_latency",
    )
    df, _ = inject_incident(base_data(), inc, seed=8)
    result = diagnose_incident(df, inc)
    assert result["evidence"]["p95_latency_ms"] > 500
    assert any(h["root_cause_type"] == "latency_spike" for h in result["ranked_hypotheses"])


def test_empty_or_invalid_schema_rejected():
    try:
        extract_incident_evidence(pd.DataFrame({"timestamp": []}), "2026-01-01", "2026-01-01T01:00:00")
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
