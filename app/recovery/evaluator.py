from __future__ import annotations

from typing import Any


def evaluate_recovery(
    revenue_at_risk: float,
    eligible_revenue: float,
    recovered_revenue: float,
    failed_transactions: int,
    recovered_transactions: int,
    eligible_transactions: int,
) -> dict[str, Any]:
    """
    Evaluate the financial impact of the recovery action.

    This compares the original revenue at risk with the amount
    successfully recovered by the bounded recovery simulation.
    """

    if revenue_at_risk < 0:
        raise ValueError("revenue_at_risk cannot be negative")

    if eligible_revenue < 0:
        raise ValueError("eligible_revenue cannot be negative")

    if recovered_revenue < 0:
        raise ValueError("recovered_revenue cannot be negative")

    if recovered_revenue > eligible_revenue:
        raise ValueError(
            "recovered_revenue cannot exceed eligible_revenue"
        )

    if recovered_revenue > revenue_at_risk:
        raise ValueError(
            "recovered_revenue cannot exceed revenue_at_risk"
        )

    if failed_transactions < 0:
        raise ValueError(
            "failed_transactions cannot be negative"
        )

    if recovered_transactions < 0:
        raise ValueError(
            "recovered_transactions cannot be negative"
        )

    if eligible_transactions < 0:
        raise ValueError(
            "eligible_transactions cannot be negative"
        )

    # Financial recovery as a percentage of total revenue at risk.
    revenue_recovery_rate = (
        recovered_revenue / revenue_at_risk
        if revenue_at_risk > 0
        else 0.0
    )

    # Recovery success rate among transactions selected for recovery.
    transaction_recovery_rate = (
        recovered_transactions / eligible_transactions
        if eligible_transactions > 0
        else 0.0
    )

    # Money still at risk after the simulated recovery.
    remaining_revenue_at_risk = max(
        revenue_at_risk - recovered_revenue,
        0.0,
    )

    # Portion of eligible recovery value that was successfully recovered.
    eligible_recovery_rate = (
        recovered_revenue / eligible_revenue
        if eligible_revenue > 0
        else 0.0
    )

    return {
        "revenue_at_risk": float(revenue_at_risk),
        "eligible_revenue": float(eligible_revenue),
        "recovered_revenue": float(recovered_revenue),
        "remaining_revenue_at_risk": float(
            remaining_revenue_at_risk
        ),
        "failed_transactions": int(failed_transactions),
        "eligible_transactions": int(eligible_transactions),
        "recovered_transactions": int(recovered_transactions),
        "revenue_recovery_rate": float(
            revenue_recovery_rate
        ),
        "eligible_recovery_rate": float(
            eligible_recovery_rate
        ),
        "transaction_recovery_rate": float(
            transaction_recovery_rate
        ),
    }