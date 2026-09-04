import pandas as pd

from app.recovery.revenue import calculate_revenue_at_risk


def make_transactions():
    return pd.DataFrame([
        {
            "transaction_id": "txn_1",
            "timestamp": "2026-01-01 01:05:00",
            "amount": 1000.0,
            "payment_method": "upi",
            "bank": "hdfc",
            "status": "failed",
        },
        {
            "transaction_id": "txn_2",
            "timestamp": "2026-01-01 01:10:00",
            "amount": 2000.0,
            "payment_method": "upi",
            "bank": "sbi",
            "status": "failed",
        },
        {
            "transaction_id": "txn_3",
            "timestamp": "2026-01-01 01:15:00",
            "amount": 3000.0,
            "payment_method": "card",
            "bank": "hdfc",
            "status": "failed",
        },
        {
            "transaction_id": "txn_4",
            "timestamp": "2026-01-01 01:20:00",
            "amount": 4000.0,
            "payment_method": "upi",
            "bank": "hdfc",
            "status": "success",
        },
    ])


def test_revenue_at_risk_counts_failed_transactions():
    df = make_transactions()

    result = calculate_revenue_at_risk(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
    )

    assert result["failed_transactions"] == 3
    assert result["revenue_at_risk"] == 6000.0


def test_revenue_at_risk_filters_payment_method():
    df = make_transactions()

    result = calculate_revenue_at_risk(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
    )

    assert result["failed_transactions"] == 2
    assert result["revenue_at_risk"] == 3000.0


def test_empty_dataframe():
    df = pd.DataFrame()

    result = calculate_revenue_at_risk(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
    )

    assert result["revenue_at_risk"] == 0.0
    assert result["failed_transactions"] == 0