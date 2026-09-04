from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


PAYMENT_METHODS = ["upi", "card", "netbanking", "wallet"]
BANKS = ["hdfc", "sbi", "icici", "axis", "kotak", "yes_bank"]
REGIONS = ["north", "south", "east", "west"]
MERCHANTS = [f"merchant_{i:03d}" for i in range(1, 21)]

METHOD_WEIGHTS = {
    "upi": 0.48,
    "card": 0.30,
    "netbanking": 0.14,
    "wallet": 0.08,
}

BANK_WEIGHTS = {
    "hdfc": 0.23,
    "sbi": 0.22,
    "icici": 0.19,
    "axis": 0.17,
    "kotak": 0.11,
    "yes_bank": 0.08,
}

REGION_WEIGHTS = {
    "north": 0.32,
    "south": 0.28,
    "west": 0.23,
    "east": 0.17,
}


@dataclass(frozen=True)
class SimulationConfig:
    start: str = "2026-01-01 00:00:00"
    minutes: int = 180
    seed: int = 42
    base_transactions_per_minute: int = 120


def _traffic_multiplier(hour: int) -> float:
    """Smoothly approximate daily payment traffic instead of flat random traffic."""
    if 0 <= hour < 6:
        return 0.35
    if 6 <= hour < 9:
        return 0.65
    if 9 <= hour < 12:
        return 1.00
    if 12 <= hour < 15:
        return 1.25
    if 15 <= hour < 18:
        return 1.10
    if 18 <= hour < 22:
        return 1.35
    return 0.75


def _method_baseline(method: str) -> tuple[float, float]:
    # success probability, mean latency in ms
    return {
        "upi": (0.975, 220),
        "card": (0.982, 180),
        "netbanking": (0.965, 300),
        "wallet": (0.978, 160),
    }[method]


def _error_for_status(rng: np.random.Generator, status: str) -> str | None:
    if status == "success":
        return None
    return rng.choice(
        ["BANK_DECLINED", "GATEWAY_ERROR", "TIMEOUT", "UPSTREAM_5XX"],
        p=[0.48, 0.20, 0.18, 0.14],
    )


def generate_transactions(config: SimulationConfig) -> pd.DataFrame:
    """Generate correlated, time-dependent synthetic payment transactions."""
    if config.minutes <= 0:
        raise ValueError("minutes must be > 0")
    if config.base_transactions_per_minute <= 0:
        raise ValueError("base_transactions_per_minute must be > 0")

    rng = np.random.default_rng(config.seed)
    timestamps = pd.date_range(
        start=config.start, periods=config.minutes, freq="min"
    )

    rows: list[dict] = []
    transaction_number = 0

    for ts in timestamps:
        multiplier = _traffic_multiplier(ts.hour)
        expected_count = config.base_transactions_per_minute * multiplier
        count = int(rng.poisson(expected_count))

        for _ in range(count):
            transaction_number += 1

            method = rng.choice(
                PAYMENT_METHODS,
                p=[METHOD_WEIGHTS[m] for m in PAYMENT_METHODS],
            )
            bank = rng.choice(
                BANKS,
                p=[BANK_WEIGHTS[b] for b in BANKS],
            )
            region = rng.choice(
                REGIONS,
                p=[REGION_WEIGHTS[r] for r in REGIONS],
            )
            merchant = rng.choice(MERCHANTS)

            base_success, base_latency = _method_baseline(method)

            # Small correlated effects: certain banks/regions are naturally
            # a little different, but no individual transaction is hardcoded.
            bank_success_adjustment = {
                "hdfc": 0.003, "sbi": -0.004, "icici": 0.002,
                "axis": 0.000, "kotak": 0.001, "yes_bank": -0.006,
            }[bank]
            region_latency_adjustment = {
                "north": 10, "south": 0, "east": 18, "west": 5,
            }[region]

            success_probability = np.clip(
                base_success + bank_success_adjustment, 0.90, 0.995
            )
            success = rng.random() < success_probability

            # Lognormal gives a realistic right tail for latency.
            latency = max(
                20.0,
                rng.lognormal(
                    mean=np.log(base_latency + region_latency_adjustment),
                    sigma=0.30,
                ),
            )

            if not success:
                latency *= rng.uniform(1.2, 2.2)

            retry_count = 0
            if not success and rng.random() < 0.35:
                retry_count = int(rng.choice([1, 2], p=[0.75, 0.25]))

            if success:
                http_status = 200
                status = "success"
            else:
                http_status = int(rng.choice([400, 408, 429, 500, 502, 504]))
                status = "failed"

            error_code = _error_for_status(rng, status)

            rows.append(
                {
                    "transaction_id": f"txn_{transaction_number:09d}",
                    "timestamp": ts,
                    "amount": round(float(rng.lognormal(np.log(850), 0.9)), 2),
                    "payment_method": method,
                    "bank": bank,
                    "merchant": merchant,
                    "region": region,
                    "status": status,
                    "latency_ms": round(float(latency), 2),
                    "http_status": http_status,
                    "error_code": error_code,
                    "retry_count": retry_count,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def save_to_sqlite(df: pd.DataFrame, db_path: str | Path) -> None:
    """Persist transactions to a simple SQL table for later detection/analytics."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        df.to_sql("transactions", conn, if_exists="replace", index=False)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_timestamp "
            "ON transactions(timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_bank "
            "ON transactions(bank)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_method "
            "ON transactions(payment_method)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RazorMind payment traffic")
    parser.add_argument("--start", default="2026-01-01 00:00:00")
    parser.add_argument("--minutes", type=int, default=180)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--base-tpm", type=int, default=120)
    parser.add_argument("--db", default="data/razormind.db")
    args = parser.parse_args()

    config = SimulationConfig(
        start=args.start,
        minutes=args.minutes,
        seed=args.seed,
        base_transactions_per_minute=args.base_tpm,
    )
    df = generate_transactions(config)
    save_to_sqlite(df, args.db)

    print(f"Generated {len(df):,} transactions")
    print(f"Saved to {args.db}")
    print("\nStatus distribution:")
    print(df["status"].value_counts(normalize=True).round(4))
    print("\nMean latency by payment method (ms):")
    print(df.groupby("payment_method")["latency_ms"].mean().round(1))


if __name__ == "__main__":
    main()
