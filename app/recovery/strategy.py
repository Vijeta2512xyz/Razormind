from __future__ import annotations

from typing import Any

import pandas as pd


DEFAULT_MAX_RETRIES = 2
DEFAULT_MAX_AMOUNT = 10_000.0


def build_recovery_strategy(
    transactions: pd.DataFrame,
    incident_start: str,
    incident_end: str,
    affected_payment_method: str | None = None,
    affected_bank: str | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    max_amount: float = DEFAULT_MAX_AMOUNT,
) -> dict[str, Any]:
    """
    Determine which failed transactions are eligible for bounded recovery.

    Safety rules:
    - transaction must be inside the incident window
    - transaction must have failed
    - payment method/bank can be restricted to the diagnosed component
    - retry_count must be below the retry limit
    - transaction amount must be below the safety limit

    Every recovery decision is recorded in the audit trail.
    """

    if transactions.empty:
        return {
            "strategy": "bounded_retry",
            "max_retries": max_retries,
            "max_amount": max_amount,
            "eligible_transactions": 0,
            "ineligible_transactions": 0,
            "eligible_revenue": 0.0,
            "transactions": [],
            "audit_trail": [],
        }

    required_columns = {
        "transaction_id",
        "timestamp",
        "amount",
        "status",
        "retry_count",
    }

    missing = required_columns - set(transactions.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if max_retries < 0:
        raise ValueError("max_retries cannot be negative")

    if max_amount <= 0:
        raise ValueError("max_amount must be greater than zero")

    df = transactions.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    start = pd.Timestamp(incident_start)
    end = pd.Timestamp(incident_end)

    mask = (
        (df["timestamp"] >= start)
        & (df["timestamp"] <= end)
    )

    mask &= (
        df["status"]
        .astype(str)
        .str.lower()
        == "failed"
    )

    if affected_payment_method is not None:
        if "payment_method" not in df.columns:
            raise ValueError(
                "payment_method column required when filtering by payment method"
            )

        mask &= (
            df["payment_method"]
            .astype(str)
            .str.lower()
            == affected_payment_method.lower()
        )

    if affected_bank is not None:
        if "bank" not in df.columns:
            raise ValueError(
                "bank column required when filtering by bank"
            )

        mask &= (
            df["bank"]
            .astype(str)
            .str.lower()
            == affected_bank.lower()
        )

    candidates = df.loc[mask].copy()

    candidates = candidates.sort_values(
        ["timestamp", "transaction_id"]
    )

    eligible_rows = []
    audit_trail = []

    for _, row in candidates.iterrows():

        transaction_id = str(row["transaction_id"])
        amount = float(row["amount"])
        retry_count = int(row["retry_count"])

        # ---------------------------------------------
        # Stopping rule 1: retry limit
        # ---------------------------------------------
        if retry_count >= max_retries:

            audit_trail.append({
                "transaction_id": transaction_id,
                "decision": "rejected",
                "reason": "retry_limit_reached",
                "amount": amount,
                "retry_count": retry_count,
                "action": "stop",
            })

            continue

        # ---------------------------------------------
        # Stopping rule 2: transaction amount limit
        # ---------------------------------------------
        if amount > max_amount:

            audit_trail.append({
                "transaction_id": transaction_id,
                "decision": "rejected",
                "reason": "amount_limit_exceeded",
                "amount": amount,
                "retry_count": retry_count,
                "action": "stop",
            })

            continue

        # ---------------------------------------------
        # Eligible transaction
        # ---------------------------------------------
        audit_trail.append({
            "transaction_id": transaction_id,
            "decision": "approved",
            "reason": "passed_safety_rules",
            "amount": amount,
            "retry_count": retry_count,
            "action": "bounded_retry",
        })

        eligible_rows.append(row)

    eligible = pd.DataFrame(eligible_rows)

    transactions_out = []

    for _, row in eligible.iterrows():

        transactions_out.append({
            "transaction_id": str(row["transaction_id"]),
            "timestamp": str(row["timestamp"]),
            "amount": float(row["amount"]),
            "payment_method": str(row.get("payment_method", "")),
            "bank": str(row.get("bank", "")),
            "retry_count": int(row["retry_count"]),
        })

    eligible_revenue = (
        float(eligible["amount"].sum())
        if not eligible.empty
        else 0.0
    )

    return {
        "strategy": "bounded_retry",
        "max_retries": max_retries,
        "max_amount": max_amount,
        "eligible_transactions": int(len(eligible)),
        "ineligible_transactions": int(
            len(candidates) - len(eligible)
        ),
        "eligible_revenue": eligible_revenue,
        "transactions": transactions_out,
        "audit_trail": audit_trail,
    }