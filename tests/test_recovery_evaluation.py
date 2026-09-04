from app.recovery.evaluator import evaluate_recovery


def test_recovery_evaluation_calculates_revenue_recovery():
    result = evaluate_recovery(
        revenue_at_risk=10000.0,
        eligible_revenue=8000.0,
        recovered_revenue=6000.0,
        failed_transactions=10,
        recovered_transactions=6,
        eligible_transactions=8,
    )

    assert result["revenue_at_risk"] == 10000.0
    assert result["eligible_revenue"] == 8000.0
    assert result["recovered_revenue"] == 6000.0
    assert result["remaining_revenue_at_risk"] == 4000.0


def test_recovery_rates_are_calculated():
    result = evaluate_recovery(
        revenue_at_risk=10000.0,
        eligible_revenue=8000.0,
        recovered_revenue=6000.0,
        failed_transactions=10,
        recovered_transactions=6,
        eligible_transactions=8,
    )

    assert result["revenue_recovery_rate"] == 0.6
    assert result["eligible_recovery_rate"] == 0.75
    assert result["transaction_recovery_rate"] == 0.75


def test_zero_revenue_does_not_cause_division_error():
    result = evaluate_recovery(
        revenue_at_risk=0.0,
        eligible_revenue=0.0,
        recovered_revenue=0.0,
        failed_transactions=0,
        recovered_transactions=0,
        eligible_transactions=0,
    )

    assert result["revenue_recovery_rate"] == 0.0
    assert result["eligible_recovery_rate"] == 0.0
    assert result["transaction_recovery_rate"] == 0.0


def test_recovered_revenue_cannot_exceed_revenue_at_risk():
    try:
        evaluate_recovery(
            revenue_at_risk=5000.0,
            eligible_revenue=5000.0,
            recovered_revenue=6000.0,
            failed_transactions=5,
            recovered_transactions=5,
            eligible_transactions=5,
        )
        assert False
    except ValueError:
        assert True


def test_recovered_revenue_cannot_exceed_eligible_revenue():
    try:
        evaluate_recovery(
            revenue_at_risk=10000.0,
            eligible_revenue=5000.0,
            recovered_revenue=6000.0,
            failed_transactions=10,
            recovered_transactions=5,
            eligible_transactions=5,
        )
        assert False
    except ValueError:
        assert True