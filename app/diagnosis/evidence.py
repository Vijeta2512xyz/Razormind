from __future__ import annotations

import pandas as pd


def _validate(df: pd.DataFrame) -> None:
    required = {
        "timestamp", "status", "latency_ms", "http_status", "error_code",
        "retry_count", "payment_method", "bank", "region",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {sorted(missing)}")


def extract_incident_evidence(
    df: pd.DataFrame,
    start_time: str | pd.Timestamp,
    end_time: str | pd.Timestamp,
) -> dict:
    """Summarize observed symptoms inside an incident window."""
    _validate(df)
    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="raise")
    start, end = pd.Timestamp(start_time), pd.Timestamp(end_time)
    window = work[work["timestamp"].between(start, end, inclusive="both")].copy()
    if window.empty:
        raise ValueError("Evidence window does not overlap transaction data")

    failed = window["status"].eq("failed")
    timeout = window["error_code"].eq("TIMEOUT") | window["http_status"].isin([408, 504])

    def dimension_summary(column: str) -> list[dict]:
        rows = []
        for value, group in window.groupby(column, dropna=False, sort=True):
            fail_rate = float(group["status"].eq("failed").mean())
            rows.append({
                "value": value,
                "transaction_count": int(len(group)),
                "failure_rate": fail_rate,
                "timeout_rate": float((group["error_code"].eq("TIMEOUT") | group["http_status"].isin([408, 504])).mean()),
                "mean_latency_ms": float(group["latency_ms"].mean()),
                "p95_latency_ms": float(group["latency_ms"].quantile(.95)),
            })
        return rows

    error_counts = window.loc[failed, "error_code"].value_counts().head(10).to_dict()
    http_counts = window.loc[failed, "http_status"].value_counts().head(10).to_dict()

    return {
        "window": {"start_time": start.isoformat(), "end_time": end.isoformat()},
        "transaction_count": int(len(window)),
        "failure_rate": float(failed.mean()),
        "timeout_rate": float(timeout.mean()),
        "mean_latency_ms": float(window["latency_ms"].mean()),
        "p95_latency_ms": float(window["latency_ms"].quantile(.95)),
        "retry_rate": float(window["retry_count"].gt(0).mean()),
        "error_counts": {str(k): int(v) for k, v in error_counts.items()},
        "http_status_counts": {str(k): int(v) for k, v in http_counts.items()},
        "by_payment_method": dimension_summary("payment_method"),
        "by_bank": dimension_summary("bank"),
        "by_region": dimension_summary("region"),
    }
