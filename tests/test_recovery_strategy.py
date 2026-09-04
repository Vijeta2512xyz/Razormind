import pandas as pd

from app.recovery.strategy import build_recovery_strategy


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
            "retry_count": 2,
        },
        {
            "transaction_id": "txn_3",
            "timestamp": "2026-01-01 01:15:00",
            "amount": 15000.0,
            "payment_method": "upi",
            "bank": "hdfc",
            "status": "failed",
            "retry_count": 0,
        },
        {
            "transaction_id": "txn_4",
            "timestamp": "2026-01-01 01:20:00",
            "amount": 3000.0,
            "payment_method": "card",
            "bank": "hdfc",
            "status": "failed",
            "retry_count": 0,
        },
    ])


def test_only_safe_transactions_are_eligible():
    df = make_transactions()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=2,
        max_amount=10000,
    )

    assert result["eligible_transactions"] == 1
    assert result["ineligible_transactions"] == 2
    assert result["eligible_revenue"] == 1000.0


def test_retry_limit_is_respected():
    df = make_transactions()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=1,
    )

    assert result["eligible_transactions"] == 1


def test_amount_limit_is_respected():
    df = make_transactions()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_amount=5000,
    )

    assert result["eligible_transactions"] == 1


def test_empty_dataframe():
    df = pd.DataFrame()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
    )

    assert result["eligible_transactions"] == 0
    assert result["eligible_revenue"] == 0.0
def test_audit_trail_records_approved_transaction():
    df = make_transactions()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=2,
        max_amount=10000,
    )

    audit = result["audit_trail"]

    approved = [
        item
        for item in audit
        if item["transaction_id"] == "txn_1"
    ][0]

    assert approved["decision"] == "approved"
    assert approved["reason"] == "passed_safety_rules"
    assert approved["action"] == "bounded_retry"


def test_audit_trail_records_rejected_transaction():
    df = make_transactions()

    result = build_recovery_strategy(
        df,
        "2026-01-01 01:00:00",
        "2026-01-01 01:30:00",
        affected_payment_method="upi",
        max_retries=2,
        max_amount=10000,
    )

    audit = result["audit_trail"]

    rejected = [
        item
        for item in audit
        if item["transaction_id"] == "txn_2"
    ][0]

    assert rejected["decision"] == "rejected"
    assert rejected["reason"] == "retry_limit_reached"
    assert rejected["action"] == "stop"