from app.recovery.executor import execute_recovery


def make_strategy():
    return {
        "strategy": "bounded_retry",
        "transactions": [
            {
                "transaction_id": "txn_1",
                "amount": 1000.0,
                "retry_count": 0,
            },
            {
                "transaction_id": "txn_2",
                "amount": 2000.0,
                "retry_count": 1,
            },
            {
                "transaction_id": "txn_3",
                "amount": 3000.0,
                "retry_count": 0,
            },
        ],
    }


def test_recovery_execution_counts_transactions():
    strategy = make_strategy()

    result = execute_recovery(
        strategy,
        recovery_probability=1.0,
        seed=42,
    )

    assert result["attempted_transactions"] == 3
    assert result["recovered_transactions"] == 3
    assert result["failed_recovery_transactions"] == 0


def test_recovery_execution_calculates_revenue():
    strategy = make_strategy()

    result = execute_recovery(
        strategy,
        recovery_probability=1.0,
        seed=42,
    )

    assert result["attempted_revenue"] == 6000.0
    assert result["recovered_revenue"] == 6000.0


def test_recovery_probability_zero_recovers_nothing():
    strategy = make_strategy()

    result = execute_recovery(
        strategy,
        recovery_probability=0.0,
        seed=42,
    )

    assert result["recovered_transactions"] == 0
    assert result["recovered_revenue"] == 0.0


def test_recovery_is_deterministic_with_same_seed():
    strategy = make_strategy()

    result_1 = execute_recovery(
        strategy,
        recovery_probability=0.70,
        seed=42,
    )

    result_2 = execute_recovery(
        strategy,
        recovery_probability=0.70,
        seed=42,
    )

    assert result_1 == result_2


def test_invalid_probability_is_rejected():
    strategy = make_strategy()

    try:
        execute_recovery(
            strategy,
            recovery_probability=1.5,
        )
        assert False
    except ValueError:
        assert True