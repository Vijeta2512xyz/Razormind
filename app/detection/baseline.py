from __future__ import annotations

import pandas as pd


def add_rolling_baseline(
    metrics: pd.DataFrame,
    value_column: str,
    window: int = 10,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Add a historical rolling mean/std baseline without looking ahead."""
    if value_column not in metrics.columns:
        raise ValueError(f"Missing value column: {value_column}")
    if window < 2:
        raise ValueError("window must be at least 2")

    min_periods = min_periods or max(2, min(window, window // 2))
    if min_periods > window:
        raise ValueError("min_periods cannot exceed window")

    work = metrics.copy().sort_values("timestamp").reset_index(drop=True)
    history = work[value_column].shift(1)
    work[f"{value_column}_baseline_mean"] = history.rolling(window, min_periods=min_periods).mean()
    work[f"{value_column}_baseline_std"] = history.rolling(window, min_periods=min_periods).std(ddof=0)
    return work


def add_ewma_baseline(
    metrics: pd.DataFrame,
    value_column: str,
    span: int = 10,
) -> pd.DataFrame:
    """Add a lagged exponentially weighted moving average."""
    if value_column not in metrics.columns:
        raise ValueError(f"Missing value column: {value_column}")
    if span < 2:
        raise ValueError("span must be at least 2")

    work = metrics.copy().sort_values("timestamp").reset_index(drop=True)
    work[f"{value_column}_ewma"] = work[value_column].shift(1).ewm(span=span, adjust=False).mean()
    return work
