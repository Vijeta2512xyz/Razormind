from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IncidentConfig:
    """Ground-truth description of an injected incident."""
    incident_id: str
    incident_type: str
    start_time: str
    end_time: str
    severity: str
    affected_component: str
    affected_bank: str | None = None
    affected_payment_method: str | None = None
    affected_region: str | None = None
    expected_symptoms: tuple[str, ...] = field(default_factory=tuple)


VALID_INCIDENT_TYPES = {
    "upi_degradation",
    "bank_failure",
    "latency_spike",
    "gateway_failure",
    "timeout_spike",
    "regional_degradation",
}


def _validate_incident(df: pd.DataFrame, incident: IncidentConfig) -> pd.Series:
    required = {
        "timestamp", "status", "latency_ms", "http_status",
        "error_code", "retry_count", "payment_method", "bank", "region",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {sorted(missing)}")

    if incident.incident_type not in VALID_INCIDENT_TYPES:
        raise ValueError(f"Unsupported incident type: {incident.incident_type}")

    start = pd.Timestamp(incident.start_time)
    end = pd.Timestamp(incident.end_time)
    if start >= end:
        raise ValueError("start_time must be earlier than end_time")

    mask = pd.to_datetime(df["timestamp"]).between(start, end, inclusive="both")
    if not mask.any():
        raise ValueError("Incident window does not overlap the transaction data")
    return mask


def _apply_failure_degradation(
    df: pd.DataFrame,
    mask: pd.Series,
    rng: np.random.Generator,
    failure_probability: float,
    latency_multiplier: float,
    error_codes: list[str],
    http_statuses: list[int],
) -> None:
    """Convert a controlled fraction of successes into failures and raise latency."""
    indices = df.index[mask]
    success_indices = df.index[mask & (df["status"] == "success")]
    n_new_failures = int(np.floor(len(success_indices) * failure_probability))

    if n_new_failures > 0:
        selected = rng.choice(success_indices.to_numpy(), size=n_new_failures, replace=False)
        df.loc[selected, "status"] = "failed"
        df.loc[selected, "http_status"] = rng.choice(http_statuses, size=n_new_failures)
        df.loc[selected, "error_code"] = rng.choice(error_codes, size=n_new_failures)
        df.loc[selected, "retry_count"] = rng.choice(
            [1, 2, 3], size=n_new_failures, p=[0.55, 0.35, 0.10]
        )

    if len(indices):
        df.loc[indices, "latency_ms"] = (
            df.loc[indices, "latency_ms"]
            * rng.lognormal(mean=np.log(latency_multiplier), sigma=0.10, size=len(indices))
        ).round(2)


def inject_upi_degradation(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    out = df.copy()
    mask = _validate_incident(out, incident)
    target = mask & (out["payment_method"] == "upi")
    _apply_failure_degradation(
        out, target, rng, 0.55, 1.8,
        ["BANK_DECLINED", "TIMEOUT", "UPI_PROVIDER_ERROR"], [408, 502, 504],
    )
    return out


def inject_bank_failure(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    if not incident.affected_bank:
        raise ValueError("bank_failure requires affected_bank")
    out = df.copy()
    mask = _validate_incident(out, incident)
    target = mask & (out["bank"] == incident.affected_bank)
    _apply_failure_degradation(
        out, target, rng, 0.65, 1.7,
        ["BANK_DECLINED", "BANK_UNAVAILABLE", "TIMEOUT"], [408, 500, 502, 504],
    )
    return out


def inject_latency_spike(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    out = df.copy()
    mask = _validate_incident(out, incident)
    indices = out.index[mask]
    out.loc[indices, "latency_ms"] = (
        out.loc[indices, "latency_ms"]
        * rng.lognormal(mean=np.log(2.4), sigma=0.12, size=len(indices))
    ).round(2)

    candidates = out.index[mask & (out["status"] == "success")]
    n_timeouts = int(np.floor(len(candidates) * 0.12))
    if n_timeouts:
        selected = rng.choice(candidates.to_numpy(), size=n_timeouts, replace=False)
        out.loc[selected, "status"] = "failed"
        out.loc[selected, "http_status"] = 504
        out.loc[selected, "error_code"] = "TIMEOUT"
        out.loc[selected, "retry_count"] = rng.choice([1, 2], size=n_timeouts, p=[0.7, 0.3])
    return out


def inject_gateway_failure(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    out = df.copy()
    mask = _validate_incident(out, incident)
    _apply_failure_degradation(
        out, mask, rng, 0.50, 1.5,
        ["GATEWAY_ERROR", "UPSTREAM_5XX"], [500, 502, 503],
    )
    return out


def inject_timeout_spike(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    out = df.copy()
    mask = _validate_incident(out, incident)
    indices = out.index[mask]
    candidates = out.index[mask & (out["status"] == "success")]
    n_timeouts = int(np.floor(len(candidates) * 0.35))

    if n_timeouts:
        selected = rng.choice(candidates.to_numpy(), size=n_timeouts, replace=False)
        out.loc[selected, "status"] = "failed"
        out.loc[selected, "http_status"] = rng.choice([408, 504], size=n_timeouts)
        out.loc[selected, "error_code"] = "TIMEOUT"
        out.loc[selected, "retry_count"] = rng.choice(
            [1, 2, 3], size=n_timeouts, p=[0.40, 0.45, 0.15]
        )

    out.loc[indices, "latency_ms"] = (
        out.loc[indices, "latency_ms"]
        * rng.lognormal(mean=np.log(1.35), sigma=0.08, size=len(indices))
    ).round(2)
    return out


def inject_regional_degradation(df: pd.DataFrame, incident: IncidentConfig, rng: np.random.Generator) -> pd.DataFrame:
    if not incident.affected_region:
        raise ValueError("regional_degradation requires affected_region")
    out = df.copy()
    mask = _validate_incident(out, incident)
    target = mask & (out["region"] == incident.affected_region)
    _apply_failure_degradation(
        out, target, rng, 0.50, 1.8,
        ["REGION_UNAVAILABLE", "TIMEOUT", "UPSTREAM_5XX"], [408, 502, 503, 504],
    )
    return out


_INJECTORS: dict[str, Callable[[pd.DataFrame, IncidentConfig, np.random.Generator], pd.DataFrame]] = {
    "upi_degradation": inject_upi_degradation,
    "bank_failure": inject_bank_failure,
    "latency_spike": inject_latency_spike,
    "gateway_failure": inject_gateway_failure,
    "timeout_spike": inject_timeout_spike,
    "regional_degradation": inject_regional_degradation,
}


def inject_incident(
    df: pd.DataFrame,
    incident: IncidentConfig,
    seed: int = 42,
) -> tuple[pd.DataFrame, IncidentConfig]:
    """Inject one controlled incident and return modified data plus ground truth."""
    rng = np.random.default_rng(seed)
    modified = _INJECTORS[incident.incident_type](df, incident, rng)
    modified = modified.sort_values("timestamp").reset_index(drop=True)
    return modified, incident


def inject_incidents(
    df: pd.DataFrame,
    incidents: list[IncidentConfig],
    seed: int = 42,
) -> tuple[pd.DataFrame, list[IncidentConfig]]:
    """Apply multiple incidents sequentially with deterministic independent seeds."""
    result = df.copy()
    for offset, incident in enumerate(incidents):
        result, _ = inject_incident(result, incident, seed=seed + offset)
    return result, incidents
