import pandas as pd

from app.recovery.pipeline import run_recovery_pipeline


def make_transactions():
    return pd.DataFrame([
        {
            "transaction_id": "txn_1",
            "timestamp": "2026-01-01 01:05:00",
            "amount": 1000.0,
            "payment_method": "upi",
            "bank": "hdfc",
            "status": "failed",
            "retry_count": 0,
        },
        {
            "transaction_id": "txn_2",
            "timestamp": "2026-01-01 01:10:00",
            "amount": 2000.0,
            "payment_method": "upi",
            "bank": "sbi",
            "status": "failed",
            "retry_count": 0,
        },
        {
            "transaction_id": "txn_3",
            "timestamp": "2026-01-01 01:15:00",
            "amount": 3000.0,
            "payment_method": "card",
            "bank": "hdfc",
            "status": "failed",
            "retry_count": 0,
        },
        {
            "transaction_id": "txn_4",
            "timestamp": "2026-01-01 01:20:00",
            "amount": 4000.0,
            "payment_method": "upi",
            "bank": "hdfc",
            "status": "success",
            "retry_count": 0,
        },
    ])


def test_recovery_pipeline_runs_end_to_end():
    df = make_transactions()

    result = run_recovery_pipeline(
        transactions=df,
        incident_start="2026-01-01 01:00:00",
        incident_end="2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=2,
        max_amount=10000,
        recovery_probability=1.0,
        seed=42,
    )

    assert "revenue_risk" in result
    assert "strategy" in result
    assert "execution" in result
    assert "evaluation" in result


def test_recovery_pipeline_calculates_expected_values():
    df = make_transactions()

    result = run_recovery_pipeline(
        transactions=df,
        incident_start="2026-01-01 01:00:00",
        incident_end="2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=2,
        max_amount=10000,
        recovery_probability=1.0,
        seed=42,
    )

    evaluation = result["evaluation"]

    assert evaluation["revenue_at_risk"] == 3000.0
    assert evaluation["eligible_revenue"] == 3000.0
    assert evaluation["recovered_revenue"] == 3000.0
    assert evaluation["remaining_revenue_at_risk"] == 0.0
    assert evaluation["recovered_transactions"] == 2