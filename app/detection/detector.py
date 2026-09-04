from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .baseline import add_rolling_baseline


DEFAULT_RULES = {
    "failure_rate": {"direction": "high", "z_threshold": 3.0, "absolute_threshold": 0.08},
    "timeout_rate": {"direction": "high", "z_threshold": 3.0, "absolute_threshold": 0.03},
    "p95_latency_ms": {"direction": "high", "z_threshold": 3.0, "absolute_threshold": 1.50},
    "retry_rate": {"direction": "high", "z_threshold": 3.0, "absolute_threshold": 0.05},
}


def detect_anomalies(
    metrics: pd.DataFrame,
    value_columns: Iterable[str] | None = None,
    window: int = 10,
    z_threshold: float = 3.0,
    min_absolute_change: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Detect high-side metric anomalies using a strictly historical rolling baseline."""
    if metrics.empty:
        return metrics.copy().assign(
            anomaly_score=pd.Series(dtype=float),
            is_anomaly=pd.Series(dtype=bool),
            anomaly_reasons=pd.Series(dtype=str),
        )
    if "timestamp" not in metrics.columns:
        raise ValueError("metrics must contain timestamp")

    value_columns = list(value_columns or DEFAULT_RULES.keys())
    missing = set(value_columns) - set(metrics.columns)
    if missing:
        raise ValueError(f"Missing metric columns: {sorted(missing)}")
    if window < 2:
        raise ValueError("window must be at least 2")
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")

    work = metrics.copy().sort_values("timestamp").reset_index(drop=True)
    reasons: list[list[str]] = [[] for _ in range(len(work))]
    scores = np.zeros(len(work), dtype=float)
    flags = np.zeros(len(work), dtype=bool)
    absolute = min_absolute_change or {}

    for column in value_columns:
        work = add_rolling_baseline(work, column, window=window)
        mean_col = f"{column}_baseline_mean"
        std_col = f"{column}_baseline_std"
        baseline = work[mean_col]
        std = work[std_col]
        deviation = work[column] - baseline
        z = deviation / std.replace(0, np.nan)

        threshold = absolute.get(column)
        if threshold is None:
            threshold = DEFAULT_RULES.get(column, {}).get("absolute_threshold", 0.0)

        triggered = (z >= z_threshold) & (deviation >= threshold) & baseline.notna()
        zero_std_triggered = (std == 0) & (deviation >= threshold) & baseline.notna()
        triggered = triggered | zero_std_triggered

        for idx in np.flatnonzero(triggered.to_numpy()):
            reasons[idx].append(column)

        finite_z = z.replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=0)
        scores = np.maximum(scores, finite_z.to_numpy())
        flags |= triggered.to_numpy()

    work["anomaly_score"] = scores
    work["is_anomaly"] = flags
    work["anomaly_reasons"] = [", ".join(r) for r in reasons]
    return work
