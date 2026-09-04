import sqlite3

import pandas as pd

from app.simulator.generator import SimulationConfig, generate_transactions, save_to_sqlite


EXPECTED_COLUMNS = {
    "transaction_id", "timestamp", "amount", "payment_method", "bank",
    "merchant", "region", "status", "latency_ms", "http_status",
    "error_code", "retry_count",
}


def test_generator_is_reproducible():
    config = SimulationConfig(minutes=30, seed=7, base_transactions_per_minute=50)
    first = generate_transactions(config)
    second = generate_transactions(config)

    pd.testing.assert_frame_equal(first, second)


def test_schema_and_basic_invariants():
    df = generate_transactions(
        SimulationConfig(minutes=20, seed=1, base_transactions_per_minute=40)
    )

    assert EXPECTED_COLUMNS.issubset(df.columns)
    assert df["transaction_id"].is_unique
    assert (df["amount"] > 0).all()
    assert (df["latency_ms"] > 0).all()
    assert (df["retry_count"] >= 0).all()
    assert set(df["status"].unique()) <= {"success", "failed"}
    assert set(df["payment_method"].unique()) <= {
        "upi", "card", "netbanking", "wallet"
    }


def test_failure_records_have_error_information():
    df = generate_transactions(
        SimulationConfig(minutes=30, seed=2, base_transactions_per_minute=50)
    )
    failures = df[df["status"] == "failed"]

    assert len(failures) > 0
    assert failures["error_code"].notna().all()
    assert (failures["http_status"] != 200).all()


def test_sqlite_persistence(tmp_path):
    db = tmp_path / "test.db"
    df = generate_transactions(
        SimulationConfig(minutes=10, seed=3, base_transactions_per_minute=30)
    )
    save_to_sqlite(df, db)

    with sqlite3.connect(db) as conn:
        row_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        index_names = {
            row[1] for row in conn.execute("PRAGMA index_list('transactions')")
        }

    assert row_count == len(df)
    assert "idx_transactions_timestamp" in index_names
    assert "idx_transactions_bank" in index_names
