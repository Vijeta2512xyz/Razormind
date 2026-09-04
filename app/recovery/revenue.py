from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_revenue_at_risk(
    transactions: pd.DataFrame,
    incident_start: str,
    incident_end: str,
    affected_payment_method: str | None = None,
    affected_bank: str | None = None,
) -> dict[str, Any]:
    """
    Calculate revenue at risk from failed transactions during an incident.
    """

    if transactions.empty:
        return {
            "revenue_at_risk": 0.0,
            "failed_transactions": 0,
            "eligible_transactions": 0,
        }

    required_columns = {
        "timestamp",
        "amount",
        "status",
    }

    missing = required_columns - set(transactions.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = transactions.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    start = pd.Timestamp(incident_start)
    end = pd.Timestamp(incident_end)

    mask = (
        (df["timestamp"] >= start)
        & (df["timestamp"] <= end)
    )

    if affected_payment_method is not None:
        if "payment_method" not in df.columns:
            raise ValueError(
                "payment_method column required when filtering by payment method"
            )

        mask &= (
            df["payment_method"].astype(str).str.lower()
            == affected_payment_method.lower()
        )

    if affected_bank is not None:
        if "bank" not in df.columns:
            raise ValueError(
                "bank column required when filtering by bank"
            )

        mask &= (
            df["bank"].astype(str).str.lower()
            == affected_bank.lower()
        )

    incident_df = df.loc[mask].copy()

    failed = incident_df[
        incident_df["status"].astype(str).str.lower() == "failed"
    ].copy()

    revenue_at_risk = float(failed["amount"].sum())

    return {
        "revenue_at_risk": revenue_at_risk,
        "failed_transactions": int(len(failed)),
        "eligible_transactions": int(len(incident_df)),
        "incident_start": incident_start,
        "incident_end": incident_end,
        "affected_payment_method": affected_payment_method,
        "affected_bank": affected_bank,
    }