from __future__ import annotations

import random
from typing import Any


def execute_recovery(
    strategy: dict[str, Any],
    recovery_probability: float = 0.70,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Execute a bounded recovery simulation.

    This does NOT call a real payment provider.
    It simulates one recovery attempt for each eligible transaction.
    """

    if not 0 <= recovery_probability <= 1:
        raise ValueError(
            "recovery_probability must be between 0 and 1"
        )

    if "transactions" not in strategy:
        raise ValueError(
            "strategy must contain a transactions list"
        )

    transactions = strategy["transactions"]

    rng = random.Random(seed)

    results = []

    recovered_count = 0
    failed_count = 0
    recovered_revenue = 0.0
    attempted_revenue = 0.0

    for transaction in transactions:

        transaction_id = transaction["transaction_id"]
        amount = float(transaction["amount"])

        attempted_revenue += amount

        recovered = rng.random() < recovery_probability

        if recovered:
            recovered_count += 1
            recovered_revenue += amount
            status = "recovered"
        else:
            failed_count += 1
            status = "recovery_failed"

        results.append(
            {
                "transaction_id": transaction_id,
                "amount": amount,
                "status": status,
                "original_retry_count": transaction["retry_count"],
                "recovery_attempts": 1,
            }
        )

    attempted_count = len(transactions)

    recovery_rate = (
        recovered_count / attempted_count
        if attempted_count > 0
        else 0.0
    )

    return {
        "strategy": strategy.get(
            "strategy",
            "bounded_retry"
        ),
        "attempted_transactions": attempted_count,
        "recovered_transactions": recovered_count,
        "failed_recovery_transactions": failed_count,
        "attempted_revenue": attempted_revenue,
        "recovered_revenue": recovered_revenue,
        "recovery_rate": recovery_rate,
        "recovery_probability": recovery_probability,
        "seed": seed,
        "results": results,
    }