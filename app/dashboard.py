from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from app.detection.metrics import compute_metrics
from app.diagnosis.root_cause import diagnose_incident
from app.rag.retriever import RunbookRetriever
from app.llm.analyst import analyze, make_ollama_call
from app.simulator.incidents import IncidentConfig
from app.recovery.pipeline import run_recovery_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "data" / "razormind.db"
RUNBOOK_INDEX = PROJECT_ROOT / "app" / "rag" / "knowledge_base" / "index.json"


def load_transactions(db_path: str | Path) -> pd.DataFrame:
    with sqlite3.connect(str(db_path)) as conn:
        return pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp", conn, parse_dates=["timestamp"])


def load_runbooks() -> RunbookRetriever:
    if not RUNBOOK_INDEX.exists():
        raise FileNotFoundError(f"Runbook index not found: {RUNBOOK_INDEX}")
    return RunbookRetriever.from_json(RUNBOOK_INDEX)


def build_dashboard_snapshot(df: pd.DataFrame, frequency: str = "1min") -> dict[str, Any]:
    metrics = compute_metrics(df, frequency=frequency)
    if metrics.empty:
        return {"metrics": metrics, "latest": {}}
    latest = metrics.iloc[-1].to_dict()
    return {"metrics": metrics, "latest": latest}


def run_incident_analysis(df: pd.DataFrame, incident: IncidentConfig, top_k: int = 3) -> dict[str, Any]:
    diagnosis = diagnose_incident(df, incident)
    hypothesis = diagnosis["leading_hypothesis"]
    query = " ".join([
        incident.incident_type,
        incident.affected_component,
        hypothesis.get("root_cause_type", ""),
        hypothesis.get("component", ""),
    ])
    runbooks = load_runbooks().search(query, top_k=top_k)
    return {"diagnosis": diagnosis, "runbooks": runbooks}


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="RazorMind", page_icon="🛡️", layout="wide")
    st.title("🛡️ RazorMind")
    st.caption("AI-powered payment reliability & incident intelligence")

    with st.sidebar:
        st.header("Data source")
        db_path = st.text_input("SQLite database", str(DEFAULT_DB))
        frequency = st.selectbox("Metric frequency", ["1min", "5min"], index=0)
        st.divider()
        st.header("Incident analysis")
        incident_id = st.text_input("Incident ID", "INC-DASH-001")
        incident_type = st.selectbox("Incident type", [
            "upi_degradation", "bank_failure", "latency_spike",
            "gateway_failure", "timeout_spike", "regional_degradation",
        ])
        start_time = st.text_input("Start time (ISO)", "")
        end_time = st.text_input("End time (ISO)", "")
        severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=2)
        component = st.text_input("Affected component", "bank:hdfc")
        affected_bank = st.text_input("Affected bank (optional)", "") or None
        affected_method = st.text_input("Affected payment method (optional)", "") or None
        affected_region = st.text_input("Affected region (optional)", "") or None

    try:
        df = load_transactions(db_path)
    except Exception as exc:
        st.error(f"Could not load transactions: {exc}")
        st.info("Generate a RazorMind SQLite database first, then enter its path in the sidebar.")
        return

    if df.empty:
        st.warning("The database contains no transactions.")
        return

    snapshot = build_dashboard_snapshot(df, frequency)
    metrics = snapshot["metrics"]
    latest = snapshot["latest"]

    st.subheader("System overview")
    cols = st.columns(5)
    cols[0].metric("Transactions", f"{len(df):,}")
    cols[1].metric("Success rate", _fmt_pct(float(df["status"].eq("success").mean())))
    cols[2].metric("Failure rate", _fmt_pct(float(df["status"].eq("failed").mean())))
    cols[3].metric("Mean latency", f"{df['latency_ms'].mean():.1f} ms")
    cols[4].metric("P95 latency", f"{df['latency_ms'].quantile(.95):.1f} ms")

    st.subheader("Reliability metrics")
    chart_cols = ["failure_rate", "timeout_rate", "retry_rate"]
    chart = metrics.set_index("timestamp")[chart_cols] * 100
    st.line_chart(chart)

    latency = metrics.set_index("timestamp")[["p50_latency_ms", "p95_latency_ms"]]
    st.line_chart(latency)

    st.subheader("Latest metric window")
    st.dataframe(pd.DataFrame([latest]), use_container_width=True)

    st.subheader("Incident analysis")
    if not start_time or not end_time:
        st.info("Enter an incident start and end time in the sidebar to run RCA + RAG analysis.")
        return

    if st.button("🔎 Analyze incident", type="primary"):
        try:
            incident = IncidentConfig(
                incident_id=incident_id,
                incident_type=incident_type,
                start_time=start_time,
                end_time=end_time,
                severity=severity,
                affected_component=component,
                affected_bank=affected_bank,
                affected_payment_method=affected_method,
                affected_region=affected_region,
            )
            result = run_incident_analysis(df, incident)
            diagnosis = result["diagnosis"]
            runbooks = result["runbooks"]
            st.session_state["analysis"] = result
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

    result = st.session_state.get("analysis")
    if not result:
        return

    diagnosis = result["diagnosis"]
    leading = diagnosis["leading_hypothesis"]
    c1, c2 = st.columns(2)
    c1.metric("Leading root cause", leading["component"])
    c2.metric("Hypothesis score", f"{leading['score']:.4f}")
    st.write(leading["reason"])

    st.markdown("**Ranked hypotheses**")
    st.dataframe(pd.DataFrame(diagnosis["ranked_hypotheses"]), use_container_width=True)

    st.markdown("**Observed evidence**")
    ev = diagnosis["evidence"]
    ec1, ec2, ec3, ec4 = st.columns(4)
    ec1.metric("Failure rate", _fmt_pct(ev["failure_rate"]))
    ec2.metric("Timeout rate", _fmt_pct(ev["timeout_rate"]))
    ec3.metric("Mean latency", f"{ev['mean_latency_ms']:.1f} ms")
    ec4.metric("P95 latency", f"{ev['p95_latency_ms']:.1f} ms")

    st.markdown("**Retrieved runbooks**")
    for item in result["runbooks"]:
        with st.expander(f"{item['title']} — score {item['score']:.3f}"):
            st.write(item["text"])

    # ---------------------------------------------------------
    # Revenue Recovery
    # ---------------------------------------------------------

    st.markdown("---")
    st.subheader("💰 Revenue Recovery")

    st.caption(
        "Bounded recovery simulation based on the diagnosed incident. "
        "No real payment provider is contacted."
    )

    recovery_col1, recovery_col2, recovery_col3 = st.columns(3)

    max_retries = recovery_col1.number_input(
        "Maximum retry count",
        min_value=0,
        max_value=5,
        value=2,
        step=1,
    )

    max_amount = recovery_col2.number_input(
        "Maximum transaction amount",
        min_value=1.0,
        value=10000.0,
        step=1000.0,
    )

    recovery_probability = recovery_col3.slider(
        "Recovery simulation probability",
        min_value=0.0,
        max_value=1.0,
        value=0.70,
        step=0.05,
    )

    if st.button("💰 Run bounded recovery", type="primary"):

        try:
            recovery = run_recovery_pipeline(
                transactions=df,
                incident_start=start_time,
                incident_end=end_time,
                affected_payment_method=affected_method,
                affected_bank=affected_bank,
                max_retries=int(max_retries),
                max_amount=float(max_amount),
                recovery_probability=float(recovery_probability),
                seed=42,
            )

            st.session_state["recovery"] = recovery

        except Exception as exc:
            st.error(f"Recovery failed: {exc}")

    recovery = st.session_state.get("recovery")

    if recovery:

        revenue_risk = recovery["revenue_risk"]
        strategy = recovery["strategy"]
        execution = recovery["execution"]
        evaluation = recovery["evaluation"]

        st.markdown("### Revenue impact")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Revenue at risk",
            f"₹{evaluation['revenue_at_risk']:,.2f}",
        )

        c2.metric(
            "Eligible revenue",
            f"₹{evaluation['eligible_revenue']:,.2f}",
        )

        c3.metric(
            "Revenue recovered",
            f"₹{evaluation['recovered_revenue']:,.2f}",
        )

        c4.metric(
            "Remaining risk",
            f"₹{evaluation['remaining_revenue_at_risk']:,.2f}",
        )

        st.markdown("### Recovery execution")

        e1, e2, e3 = st.columns(3)

        e1.metric(
            "Eligible transactions",
            f"{strategy['eligible_transactions']:,}",
        )

        e2.metric(
            "Recovered transactions",
            f"{evaluation['recovered_transactions']:,}",
        )

        e3.metric(
            "Transaction recovery rate",
            _fmt_pct(
                evaluation["transaction_recovery_rate"]
            ),
        )

        st.markdown("### Recovery outcome")

        o1, o2 = st.columns(2)

        o1.metric(
            "Revenue recovery rate",
            _fmt_pct(
                evaluation["revenue_recovery_rate"]
            ),
        )

        o2.metric(
            "Eligible revenue recovered",
            _fmt_pct(
                evaluation["eligible_recovery_rate"]
            ),
        )

        st.markdown("### Before vs after")

        comparison = pd.DataFrame({
            "Stage": [
                "Before recovery",
                "After recovery",
            ],
            "Revenue at risk": [
                evaluation["revenue_at_risk"],
                evaluation["remaining_revenue_at_risk"],
            ],
        })

        st.bar_chart(
            comparison.set_index("Stage")
        )

        with st.expander("Recovery execution details"):

            st.write(
                f"Strategy: **{strategy['strategy']}**"
            )

            st.write(
                f"Maximum retries: **{strategy['max_retries']}**"
            )

            st.write(
                f"Maximum transaction amount: "
                f"**₹{strategy['max_amount']:,.2f}**"
            )

            st.write(
                f"Attempted transactions: "
                f"**{execution['attempted_transactions']:,}**"
            )

            st.write(
                f"Recovered transactions: "
                f"**{execution['recovered_transactions']:,}**"
            )

            st.write(
                f"Recovery simulation probability: "
                f"**{execution['recovery_probability']:.0%}**"
            )

            st.dataframe(
                pd.DataFrame(execution["results"]),
                use_container_width=True,
            )

            st.markdown("### Recovery audit trail")

            audit_trail = strategy.get("audit_trail", [])

            if audit_trail:

                audit_df = pd.DataFrame(audit_trail)

                st.dataframe(
                    audit_df,
                    use_container_width=True,
                )

                approved_count = sum(
                    item["decision"] == "approved"
                    for item in audit_trail
                )

                rejected_count = sum(
                    item["decision"] == "rejected"
                    for item in audit_trail
                )

                a1, a2 = st.columns(2)

                a1.metric(
                    "Approved recovery actions",
                    f"{approved_count:,}",
                )

                a2.metric(
                    "Rejected / stopped actions",
                    f"{rejected_count:,}",
                )

            else:

                st.info(
                    "No recovery audit records available."
                )
    # ---------------------------------------------------------
    # LLM Incident Report
    # ---------------------------------------------------------

    if st.button("🤖 Generate grounded report"):
        try:
            recovery = st.session_state.get("recovery")

            report = analyze(
                diagnosis=diagnosis,
                retrieved_runbooks=result["runbooks"],
                llm_call=make_ollama_call(),
                recovery=recovery,
            )

            st.session_state["report"] = report

        except Exception as exc:
            st.error(f"LLM report failed: {exc}")
            st.info(
                "Start Ollama and set RAZORMIND_OLLAMA_MODEL "
                "if you want local LLM reporting."
            )

    if "report" in st.session_state:
        st.json(st.session_state["report"])


if __name__ == "__main__":
    main()