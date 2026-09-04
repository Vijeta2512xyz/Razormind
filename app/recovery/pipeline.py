from __future__ import annotations

from typing import Any

import pandas as pd

from app.recovery.revenue import calculate_revenue_at_risk
from app.recovery.strategy import build_recovery_strategy
from app.recovery.executor import execute_recovery
from app.recovery.evaluator import evaluate_recovery


def run_recovery_pipeline(
    transactions: pd.DataFrame,
    incident_start: str,
    incident_end: str,
    affected_payment_method: str | None = None,
    affected_bank: str | None = None,
    max_retries: int = 2,
    max_amount: float = 10_000.0,
    recovery_probability: float = 0.70,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Run the complete RazorMind recovery workflow.

    Flow:
        Revenue Risk
            ↓
        Recovery Strategy
            ↓
        Bounded Recovery Execution
            ↓
        Recovery Evaluation
    """

    # 1. Calculate revenue at risk.
    revenue_risk = calculate_revenue_at_risk(
        transactions=transactions,
        incident_start=incident_start,
        incident_end=incident_end,
        affected_payment_method=affected_payment_method,
        affected_bank=affected_bank,
    )

    # 2. Determine which failed transactions are safely retryable.
    strategy = build_recovery_strategy(
        transactions=transactions,
        incident_start=incident_start,
        incident_end=incident_end,
        affected_payment_method=affected_payment_method,
        affected_bank=affected_bank,
        max_retries=max_retries,
        max_amount=max_amount,
    )

    # 3. Execute bounded recovery simulation.
    execution = execute_recovery(
        strategy=strategy,
        recovery_probability=recovery_probability,
        seed=seed,
    )

    # 4. Evaluate financial outcome.
    evaluation = evaluate_recovery(
        revenue_at_risk=revenue_risk["revenue_at_risk"],
        eligible_revenue=strategy["eligible_revenue"],
        recovered_revenue=execution["recovered_revenue"],
        failed_transactions=revenue_risk["failed_transactions"],
        recovered_transactions=execution["recovered_transactions"],
        eligible_transactions=strategy["eligible_transactions"],
    )

    return {
        "revenue_risk": revenue_risk,
        "strategy": strategy,
        "execution": execution,
        "evaluation": evaluation,
    }