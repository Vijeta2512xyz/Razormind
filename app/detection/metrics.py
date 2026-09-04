from __future__ import annotations

from typing import Sequence
import pandas as pd

REQUIRED_COLUMNS = {"timestamp", "status", "latency_ms", "http_status", "error_code", "retry_count"}
DIMENSIONS = {"payment_method", "bank", "region", "merchant"}


def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {sorted(missing)}")


def _base_metrics(group: pd.DataFrame) -> pd.Series:
    failures = group["status"].eq("failed")
    timeouts = group["error_code"].eq("TIMEOUT") | group["http_status"].isin([408, 504])
    retried = group["retry_count"].gt(0)
    return pd.Series({
        "transaction_count": len(group),
        "success_count": int(group["status"].eq("success").sum()),
        "failure_count": int(failures.sum()),
        "success_rate": group["status"].eq("success").mean(),
        "failure_rate": failures.mean(),
        "mean_latency_ms": group["latency_ms"].mean(),
        "p50_latency_ms": group["latency_ms"].quantile(.50),
        "p95_latency_ms": group["latency_ms"].quantile(.95),
        "timeout_count": int(timeouts.sum()),
        "timeout_rate": timeouts.mean(),
        "retry_count": int(retried.sum()),
        "retry_rate": retried.mean(),
    })


def compute_metrics(df: pd.DataFrame, frequency: str = "1min", dimensions: Sequence[str] | None = None) -> pd.DataFrame:
    _validate_columns(df)
    dimensions = list(dimensions or [])
    invalid = set(dimensions) - DIMENSIONS
    if invalid:
        raise ValueError(f"Unsupported dimensions: {sorted(invalid)}")
    metric_columns = ["transaction_count", "success_count", "failure_count", "success_rate", "failure_rate", "mean_latency_ms", "p50_latency_ms", "p95_latency_ms", "timeout_count", "timeout_rate", "retry_count", "retry_rate"]
    if df.empty:
        return pd.DataFrame(columns=["timestamp", *dimensions, *metric_columns])
    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="raise")
    result = (work.groupby([pd.Grouper(key="timestamp", freq=frequency), *dimensions], dropna=False, sort=True)
              .apply(_base_metrics, include_groups=False).reset_index())
    for col in ["transaction_count", "success_count", "failure_count", "timeout_count", "retry_count"]:
        result[col] = result[col].astype(int)
    return result


def compute_global_metrics(df: pd.DataFrame, frequency: str = "1min") -> pd.DataFrame:
    return compute_metrics(df, frequency=frequency)


def compute_dimension_metrics(df: pd.DataFrame, dimension: str, frequency: str = "1min") -> pd.DataFrame:
    return compute_metrics(df, frequency=frequency, dimensions=[dimension])
