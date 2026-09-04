from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import math

from app.simulator.incidents import IncidentConfig
from .evidence import extract_incident_evidence


def _rank_dimension(rows: list[dict], overall_failure: float) -> list[dict]:
    ranked = []
    for row in rows:
        lift = row["failure_rate"] - overall_failure
        share = row["transaction_count"]
        if share <= 0:
            continue
        # Evidence score rewards both unusually high failure rate and enough traffic.
        score = max(0.0, lift) * math.sqrt(share)
        ranked.append({**row, "failure_rate_lift": float(lift), "evidence_score": float(score)})
    return sorted(ranked, key=lambda x: x["evidence_score"], reverse=True)


def diagnose_incident(
    df: pd.DataFrame,
    incident: IncidentConfig,
) -> dict:
    """Produce an evidence-backed, ranked diagnosis without using an LLM."""
    evidence = extract_incident_evidence(df, incident.start_time, incident.end_time)
    overall_failure = evidence["failure_rate"]

    bank_rank = _rank_dimension(evidence["by_bank"], overall_failure)
    method_rank = _rank_dimension(evidence["by_payment_method"], overall_failure)
    region_rank = _rank_dimension(evidence["by_region"], overall_failure)

    hypotheses: list[dict] = []
    if bank_rank:
        top = bank_rank[0]
        hypotheses.append({
            "root_cause_type": "bank_failure",
            "component": f"bank:{top['value']}",
            "score": top["evidence_score"],
            "reason": f"Bank {top['value']} has the highest failure-rate lift versus the incident window overall.",
        })
    if method_rank:
        top = method_rank[0]
        hypotheses.append({
            "root_cause_type": "payment_method_degradation",
            "component": f"payment_method:{top['value']}",
            "score": top["evidence_score"],
            "reason": f"Payment method {top['value']} has the highest failure-rate lift versus the incident window overall.",
        })
    if region_rank:
        top = region_rank[0]
        hypotheses.append({
            "root_cause_type": "regional_degradation",
            "component": f"region:{top['value']}",
            "score": top["evidence_score"],
            "reason": f"Region {top['value']} has the highest failure-rate lift versus the incident window overall.",
        })

    if evidence["timeout_rate"] >= 0.10:
        hypotheses.append({
            "root_cause_type": "timeout_spike",
            "component": "payment_timeouts",
            "score": float(evidence["timeout_rate"]),
            "reason": "Timeouts are a substantial share of transactions in the incident window.",
        })
    if evidence["p95_latency_ms"] >= 500:
        hypotheses.append({
            "root_cause_type": "latency_spike",
            "component": "payment_latency",
            "score": float(evidence["p95_latency_ms"] / 1000.0),
            "reason": "P95 latency is materially elevated in the incident window.",
        })
    if any(int(k) >= 500 for k in evidence["http_status_counts"]):
        hypotheses.append({
            "root_cause_type": "gateway_or_upstream_failure",
            "component": "gateway_or_upstream",
            "score": float(sum(v for k, v in evidence["http_status_counts"].items() if int(k) >= 500) / max(1, evidence["transaction_count"])),
            "reason": "Server-side 5xx responses are present among incident failures.",
        })

    hypotheses.sort(key=lambda x: x["score"], reverse=True)
    top = hypotheses[0] if hypotheses else {
        "root_cause_type": "unknown",
        "component": "unknown",
        "score": 0.0,
        "reason": "Insufficient evidence to rank a root cause.",
    }

    return {
        "incident_id": incident.incident_id,
        "incident_type": incident.incident_type,
        "severity": incident.severity,
        "expected_component": incident.affected_component,
        "evidence": evidence,
        "ranked_hypotheses": hypotheses,
        "leading_hypothesis": top,
        "ground_truth": asdict(incident),
    }
