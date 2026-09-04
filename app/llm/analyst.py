from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

SYSTEM_PROMPT = """You are RazorMind, an incident-response analyst.

Your job is to explain the supplied deterministic incident diagnosis AND,
when provided, the actual revenue-recovery outcome.

IMPORTANT RULES:

1. The field leading_hypothesis in the supplied incident evidence is the
   authoritative root-cause hypothesis.

2. You MUST NOT replace, reinterpret, or invent a different root cause.

3. The value of likely_root_cause in your output MUST match the supplied
   leading_hypothesis exactly.

4. Use only the supplied incident evidence, retrieved runbooks, and
   recovery_outcome.

5. Do not invent metrics, timestamps, components, causes, recovery results,
   or actions.

6. Evidence must be based on the supplied diagnosis.

7. Recommended actions should be grounded in the retrieved runbooks.

8. If recovery_outcome is supplied, treat it as authoritative.

9. If recovery_outcome is supplied, accurately describe the actual recovery
   strategy and financial outcome.

10. If recovery_outcome contains revenue at risk, eligible revenue,
    revenue recovered, remaining risk, recovery rates, transaction counts,
    or safety/audit information, use those supplied values accurately.

11. NEVER replace the actual recovery outcome with a hypothetical recovery
    recommendation.

12. NEVER invent recovery amounts, percentages, transaction counts,
    strategies, or results.

13. NEVER output placeholder values such as [summary], [root_cause],
    [component1], [component2], [evidence1], [action1], or similar.

14. Every output field must contain actual information derived from the
    supplied INPUT.

15. If recovery_outcome is present, the summary should mention the actual
    recovery result when relevant.

16. You may explain why the leading hypothesis is supported, but you may not
    change the hypothesis.

17. Return ONLY valid JSON.

18. Do not use markdown.

19. Do not add explanations outside the JSON.

The JSON must contain exactly these fields:
summary, severity, likely_root_cause, affected_components,
evidence, recommended_actions, confidence.

severity must be one of:
low, medium, high, critical.

confidence must be a number between 0 and 1.
"""


REPORT_SCHEMA = {
    "type": "object",
    "required": [
        "summary",
        "severity",
        "likely_root_cause",
        "affected_components",
        "evidence",
        "recommended_actions",
        "confidence",
    ],
    "properties": {
        "summary": {
            "type": "string"
        },
        "severity": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"]
        },
        "likely_root_cause": {
            "type": "string"
        },
        "affected_components": {
            "type": "array",
            "items": {"type": "string"}
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recommended_actions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
    },
    "additionalProperties": False,
}


@dataclass(frozen=True)
class AnalystInput:
    diagnosis: dict[str, Any]
    retrieved_runbooks: list[dict[str, Any]]
    recovery: dict[str, Any] | None = None


def build_prompt(inp: AnalystInput) -> str:
    payload = {
        "incident_evidence": inp.diagnosis,
        "retrieved_runbooks": inp.retrieved_runbooks,
        "recovery_outcome": inp.recovery,
    }

    return (
        SYSTEM_PROMPT
        + "\n\nINPUT:\n"
        + json.dumps(payload, indent=2, default=str)
    )
    payload = {
        "incident_evidence": inp.diagnosis,
        "retrieved_runbooks": inp.retrieved_runbooks,
    }

    return (
        SYSTEM_PROMPT
        + "\n\nINPUT:\n"
        + json.dumps(payload, indent=2, default=str)
    )


def _extract_json(text: str) -> str:
    """
    Extract JSON even if a local model accidentally wraps it
    in markdown or adds a small amount of extra text.
    """

    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Find the JSON object if there is extra text around it
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


def validate_report(report: dict[str, Any]) -> dict[str, Any]:
    required = {
        "summary",
        "severity",
        "likely_root_cause",
        "affected_components",
        "evidence",
        "recommended_actions",
        "confidence",
    }

    missing = required - set(report)

    if missing:
        raise ValueError(
            f"LLM report missing keys: {sorted(missing)}"
        )

    if report["severity"] not in {
        "low",
        "medium",
        "high",
        "critical",
    }:
        raise ValueError(
            "severity must be low, medium, high, or critical"
        )

    if not isinstance(report["confidence"], (int, float)):
        raise ValueError(
            "confidence must be between 0 and 1"
        )

    if not 0 <= report["confidence"] <= 1:
        raise ValueError(
            "confidence must be between 0 and 1"
        )

    for key in (
        "summary",
        "likely_root_cause",
    ):
        if not isinstance(report[key], str):
            raise ValueError(
                f"{key} must be a string"
            )

    for key in (
        "affected_components",
        "evidence",
        "recommended_actions",
    ):
        if not isinstance(report[key], list):
            raise ValueError(
                f"{key} must be a list"
            )

        if not all(isinstance(item, str) for item in report[key]):
            raise ValueError(
                f"{key} must contain only strings"
            )

    return report


def analyze(
    diagnosis: dict[str, Any],
    retrieved_runbooks: list[dict[str, Any]],
    llm_call: Callable[[str], str] | None = None,
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if llm_call is None:
        raise RuntimeError(
            "No LLM provider configured. "
            "Pass llm_call or configure a provider adapter."
        )
    if recovery is not None:

        hypothesis = diagnosis.get("leading_hypothesis", {})

        if isinstance(hypothesis, dict):
          root_cause = hypothesis.get(
            "component",
            hypothesis.get("root_cause_type", "unknown")
          )
        else:
          root_cause = str(hypothesis)

        revenue_risk = recovery.get("revenue_risk", {})
        strategy = recovery.get("strategy", {})
        execution = recovery.get("execution", {})
        evaluation = recovery.get("evaluation", {})

        revenue_at_risk = revenue_risk.get("revenue_at_risk", 0)
        failed_transactions = revenue_risk.get("failed_transactions", 0)

        strategy_name = strategy.get("strategy", "bounded_retry")
        eligible_revenue = strategy.get("eligible_revenue", 0)
        eligible_transactions = strategy.get("eligible_transactions", 0)
        ineligible_transactions = strategy.get("ineligible_transactions", 0)

        revenue_recovered = execution.get("recovered_revenue", 0)
        recovered_transactions = execution.get("recovered_transactions", 0)

        remaining_risk = evaluation.get(
          "remaining_risk",
           revenue_at_risk - revenue_recovered
        )

        affected_components = diagnosis.get("affected_components", [])

        if not affected_components:
            affected_components = [root_cause]

        return {
            "summary": (
               f"Incident {diagnosis.get('incident_id', 'unknown')} was diagnosed as "
               f"{root_cause}. Revenue at risk was "
               f"₹{revenue_at_risk:,.2f}. The {strategy_name} strategy "
               f"recovered ₹{revenue_recovered:,.2f}, leaving "
               f"₹{remaining_risk:,.2f} at risk."
            ),
            "severity": diagnosis.get("severity", "high"),
            "likely_root_cause": root_cause,
            "affected_components": affected_components,
            "evidence": [
                f"Revenue at risk: ₹{revenue_at_risk:,.2f}",
                f"Eligible recovery revenue: ₹{eligible_revenue:,.2f}",
                f"Revenue recovered: ₹{revenue_recovered:,.2f}",
                f"Remaining risk: ₹{remaining_risk:,.2f}",
                f"Recovered transactions: {recovered_transactions}",
                f"Failed transactions in incident: {failed_transactions}",
            ],
            "recommended_actions": [
               f"Recovery strategy executed: {strategy_name}",
               "Continue monitoring the affected payment flow.",
               "Escalate if recovery safety limits are repeatedly reached.",
            ],
            "confidence": 0.95,
        }

    raw_response = llm_call(
        build_prompt(
            AnalystInput(
                diagnosis=diagnosis,
                retrieved_runbooks=retrieved_runbooks,
                recovery=recovery,
            )
        )
    )

    try:
        cleaned_response = _extract_json(raw_response)
        report = json.loads(cleaned_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc

    # all your existing code here...

    return validate_report(report)



def make_ollama_call(
    model: str | None = None,
    host: str | None = None,
) -> Callable[[str], str]:

    import urllib.request

    model = model or os.getenv(
        "RAZORMIND_OLLAMA_MODEL",
        "llama3.2:3b"
    )

    host = (
        host
        or os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434"
        )
    ).rstrip("/")

    def call(prompt: str) -> str:

        body = json.dumps(
            {
                "model": model,
                "system": SYSTEM_PROMPT,
                "prompt": prompt,
                "stream": False,

                # IMPORTANT:
                # Instead of simply asking Ollama for "some JSON",
                # we give it the exact JSON structure we expect.
                "format": "json",

                "options": {
                    "temperature": 0
                },
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{host}/api/generate",
            data=body,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

            return data["response"]

    return call