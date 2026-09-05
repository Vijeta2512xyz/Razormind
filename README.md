# RazorMind

### AI-Powered Payment Reliability & Incident Intelligence

RazorMind is an end-to-end payment reliability system that detects payment incidents, diagnoses their root causes, calculates financial impact, executes bounded recovery strategies, and generates grounded incident reports.

Built for the **Razorpay AI Buildathon 2026** with a core principle:

> **Use deterministic systems for detection and control. Use AI for reasoning and explanation.**

---

## 🚨 The Problem

Payment failures are not just engineering problems.

A degraded payment method or banking component can cause:

- Increased payment failures
- Higher latency and timeouts
- Retry storms
- Revenue loss
- Difficult-to-trace incidents
- Slow manual recovery

A useful incident-response system therefore needs to answer:

1. **What is happening?**
2. **Why is it happening?**
3. **How much revenue is at risk?**
4. **What can safely be recovered?**
5. **How much revenue was actually recovered?**
6. **What should the incident-response team do next?**

RazorMind connects these steps into one pipeline.

---

# 💰 From Payment Failure → Revenue Recovery

A complete RazorMind incident flow:

```text
PAYMENT FAILURE
      ↓
DETECT
      ↓
DIAGNOSE
      ↓
💰 CALCULATE REVENUE AT RISK
      ↓
🧠 DECIDE RECOVERY STRATEGY
      ↓
⚙️ EXECUTE BOUNDED RECOVERY
      ↓
💰 MEASURE REVENUE RECOVERED
      ↓
📊 BEFORE vs AFTER
      ↓
🤖 GROUNDED LLM EXPLANATION


Demonstration run

For the demonstrated UPI degradation incident:

Metric	Result
Revenue at risk	₹450,208.78
Eligible revenue	₹286,845.77
Revenue recovered	₹191,964.11
Remaining risk	₹258,244.67
Eligible transactions	216
Recovered transactions	154
Transaction recovery rate	71.30%
Revenue recovery rate	42.64%
Eligible revenue recovered	66.92%
Recovery strategy	Bounded Retry
Maximum retries	2
Maximum transaction amount	₹10,000

Recovery is simulated and bounded. RazorMind does not make real payment-provider calls or execute unrestricted financial transactions.


🏗️ Architecture
┌──────────────────────┐
│  Payment Simulator   │
│  Transactions        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Incident Injector    │
│ Failure / Latency    │
│ Timeout / Retry      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Metrics Engine       │
│ Rates / Latency /    │
│ Timeouts / Retries   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Anomaly Detection    │
│ Rolling Baseline     │
│ Statistical Signals  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Incident Correlation │
│ Time / Method / Bank │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Root Cause Engine    │
│ Evidence-based RCA   │
└──────────┬───────────┘
           │
      ┌────┴───────────────┐
      ↓                    ↓
┌───────────────┐   ┌────────────────┐
│ Revenue Risk  │   │ RAG Runbooks   │
│ + Recovery    │   │ Retrieval      │
└───────┬───────┘   └───────┬────────┘
        │                   │
        └─────────┬─────────┘
                  ↓
          ┌───────────────┐
          │ LLM Analyst   │
          │ Grounded      │
          │ Explanation   │
          └───────┬───────┘
                  ↓
          ┌───────────────┐
          │ Streamlit UI  │
          └───────────────┘

🔄 End-to-End Workflow
1. Payment Simulation

RazorMind generates transaction-level payment data containing:

Transaction ID
Timestamp
Payment method
Bank
Amount
Status
Latency
Retry count

This provides a reproducible environment for testing incident detection and recovery.

2. Incident Injection

Controlled incidents can be injected into the transaction stream.

Examples include:

UPI degradation
Bank-specific degradation
Increased failure rates
Increased latency
Increased timeout rates
Increased retries

Each incident has structured metadata:
incident_id
incident_type
start_time
end_time
severity
affected_component
affected_payment_method
expected_symptoms
This makes incidents reproducible and measurable.
📈 3. Metrics Aggregation

RazorMind calculates operational signals such as:

Transaction volume
Success rate
Failure rate
Mean latency
P95 latency
Timeout rate
Retry rate
Payment-method performance
Bank performance

These metrics form the evidence layer for downstream detection and diagnosis.

🚨 4. Deterministic Incident Detection
The LLM is NOT the detector.

RazorMind deliberately avoids using an LLM as the primary monitoring mechanism.

Detection is based on statistical signals including:

Rolling baselines
Z-score style anomaly detection
EWMA-style monitoring
Failure-rate deviations
Latency deviations
Timeout/retry changes

This provides:

Reproducibility
Testability
Lower inference dependency
Explainable alerts
Deterministic behavior

The LLM comes later.

🔎 5. Incident Correlation

Once abnormal behavior is detected, RazorMind correlates the signals across:

Time windows
Payment methods
Banks
Failure rates
Latency
Timeouts
Retries

This narrows the investigation from:

"Payments are failing"

to something more actionable:

"UPI payments are showing abnormal failures,
latency and timeout behavior during the incident window."
🧠 6. Evidence-Based Root Cause Analysis

RazorMind creates structured evidence before involving the LLM.

Root-cause candidates can be evaluated across dimensions such as:

Payment method
Bank
Processor
Failure rate
Timeout rate
Latency
Retry behavior

The system scores candidates using observed evidence.

Example:

Leading hypothesis:
payment_method:upi

Supporting evidence:
- Failure rate increased
- Timeout rate increased
- Latency increased
- Symptoms are concentrated in UPI traffic

The important architectural decision is:

The deterministic system decides the leading hypothesis. The LLM explains it.

This prevents the LLM from inventing an unrelated root cause.

💰 7. Revenue at Risk

Incident response should not stop at:

"Failure rate increased."

RazorMind translates failures into financial impact.

Revenue at risk is calculated from failed transactions inside the affected incident window.

Conceptually:

Revenue at Risk
=
Σ amount of affected failed transactions

The calculation can also be restricted using incident attributes such as:

Payment method
Bank
Incident time window

This connects operational monitoring directly to business impact.

⚙️ 8. Bounded Recovery Strategy

RazorMind does not blindly retry every failed payment.

Every candidate transaction passes safety checks.

Recovery constraints
✓ Inside incident window
✓ Transaction failed
✓ Matches affected payment method
✓ Matches affected bank when applicable
✓ Retry count below maximum
✓ Transaction amount below maximum

Example strategy:

Maximum retries:       2
Maximum amount:        ₹10,000
Strategy:              bounded_retry

Transactions that violate safety rules are stopped.

🛡️ 9. Recovery Audit Trail

Every candidate transaction receives an audit decision.

Example:

Candidate transaction
        ↓
Safety checks
        ↓
 ┌───────────────┐
 │ Pass          │ ───→ bounded retry
 └───────────────┘

 ┌───────────────┐
 │ Fail          │ ───→ stop + reason
 └───────────────┘

Possible rejection reasons include:

retry_limit_reached
amount_limit_exceeded

This gives the recovery system a clear control boundary.

Demonstrated run
Candidate transactions evaluated: 360
Approved recovery actions:       216
Stopped/rejected actions:        144

Only approved transactions are sent to the simulated recovery executor.

💵 10. Recovery Execution

Recovery execution is intentionally simulated.

For each eligible transaction:

Eligible transaction
        ↓
One bounded retry attempt
        ↓
Recovery success / failure

The executor uses a configurable recovery probability for simulation.

It does not:

Call a real payment gateway
Move real money
Perform unrestricted retries
Automatically modify external financial systems

This makes the system safe to demonstrate while still allowing realistic recovery evaluation.

📊 11. Recovery Evaluation

RazorMind measures both operational and financial recovery.

Metrics include:

Revenue recovered
Remaining revenue risk
Revenue recovery rate
Eligible revenue recovery rate
Transaction recovery rate
Recovered transaction count
Failed transaction count

Example:

Revenue at risk        ₹450,208.78
        ↓
Eligible revenue       ₹286,845.77
        ↓
Recovered revenue      ₹191,964.11
        ↓
Remaining risk         ₹258,244.67

This makes recovery measurable instead of simply claiming that an automated action was executed.

📚 12. RAG Runbook Retrieval

RazorMind includes a lightweight Retrieval-Augmented Generation pipeline.

Runbooks
   ↓
Document processing
   ↓
Searchable representation
   ↓
Similarity retrieval
   ↓
Relevant runbooks
   ↓
LLM context

Runbooks cover operational scenarios such as:

UPI degradation
Bank failures
Processor failures
Gateway issues
Latency problems
Timeout problems

The retriever uses a lightweight TF-IDF + cosine similarity approach.

This keeps the project easy to run locally while demonstrating the complete RAG architecture.

🤖 13. Grounded LLM Incident Analyst

The LLM receives structured context from the system:

Incident evidence
        +
Root-cause diagnosis
        +
Retrieved runbooks
        +
Revenue impact
        +
Recovery strategy
        +
Recovery outcome

It generates structured incident analysis containing:

summary
severity
likely_root_cause
affected_components
evidence
recommended_actions
confidence

The LLM is explicitly constrained to:

Use the supplied deterministic diagnosis
Preserve the leading root-cause hypothesis
Use retrieved runbook context
Use actual recovery results
Avoid inventing metrics
Avoid inventing financial outcomes
Return structured JSON


🎯 Core Design Philosophy
LLM FOR REASONING AND EXPLANATION
NOT LLM FOR BASIC MONITORING
Raw Transactions
       ↓
Deterministic Metrics
       ↓
Statistical Detection
       ↓
Structured Diagnosis
       ↓
Revenue Impact
       ↓
Bounded Recovery
       ↓
RAG Context
       ↓
LLM Explanation

This separation improves:

Reliability
Reproducibility
Explainability
Testability
Grounding
Safety


🖥️ Dashboard

The Streamlit dashboard provides a complete incident investigation workflow.

It surfaces:

Incident details
Detection signals
Root-cause diagnosis
Supporting evidence
Revenue at risk
Recovery strategy
Recovery results
Before/after metrics
Retrieved runbooks
LLM incident analysis
Screenshots

Place your screenshots inside:

docs/
└── screenshots/
    ├── dashboard.png
    ├── recovery.png
    └── diagnosis.png

Then they can be displayed here:

![RazorMind Dashboard](docs/screenshots/dashboard.png)

![Recovery Analysis](docs/screenshots/recovery.png)

![Incident Diagnosis](docs/screenshots/diagnosis.png)


🧪 Testing

RazorMind has a full automated test suite covering the major system components.

86 tests passed

Run:

python -m pytest -q

Coverage includes:

Simulation
Incident injection
Metrics
Detection
Diagnosis / RCA
RAG
LLM analyst
Evaluation
Revenue calculation
Recovery strategy
Recovery executor
Recovery evaluation
Recovery pipeline

The goal is not only to demonstrate that the dashboard works, but that the underlying incident-response logic is independently testable.


🧰 Tech Stack
Core
Python
Pandas
NumPy
SQLite
Detection & Retrieval
Statistical anomaly detection
Rolling baselines
Z-score style detection
EWMA-style monitoring
TF-IDF
Cosine similarity
AI
Ollama
Local LLM inference
Retrieval-Augmented Generation
Grounded structured generation
Interface
Streamlit
Testing
Pytest


📁 Project Structure
razormind/
│
├── app/
│   ├── __init__.py
│   │
│   ├── simulator/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   ├── incidents.py
│   │   └── schema.sql
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── baseline.py
│   │   └── detector.py
│   │
│   ├── diagnosis/
│   │   ├── __init__.py
│   │   ├── evidence.py
│   │   └── root_cause.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── knowledge_base/
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── analyst.py
│   │
│   ├── recovery/
│   │   ├── __init__.py
│   │   ├── revenue.py
│   │   ├── strategy.py
│   │   ├── executor.py
│   │   ├── evaluator.py
│   │   └── pipeline.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── detection_metrics.py
│   │   ├── diagnosis_metrics.py
│   │   └── evaluation_runner.py
│   │
│   └── dashboard.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── razormind.db
│
├── models/
│
├── notebooks/
│
├── tests/
│   ├── test_generator.py
│   ├── test_incidents.py
│   ├── test_detection.py
│   ├── test_diagnosis.py
│   ├── test_rag.py
│   ├── test_llm.py
│   ├── test_evaluation.py
│   └── test_recovery.py
│
├── requirements.txt
├── README.md
└── .gitignore


🚀 Getting Started
1. Clone
git clone https://github.com/Vijeta2512xyz/Razormind.git
cd Razormind
2. Install dependencies
pip install -r requirements.txt
3. Run the test suite
python -m pytest -q

Expected:

86 passed
4. Launch the dashboard
streamlit run app/dashboard.py


🤖 Optional Local LLM Setup

RazorMind can use Ollama for local LLM-based incident reporting.

For PowerShell:

$env:PYTHONPATH=(Get-Location).Path
$env:RAZORMIND_OLLAMA_MODEL="phi:latest"
streamlit run app/dashboard.py

Make sure Ollama is running and the selected model is available locally.

The core detection, diagnosis, recovery, and evaluation pipeline does not depend on an external hosted LLM.


🔐 Safety & Production Considerations

RazorMind is intentionally designed as a controlled prototype.

The recovery layer is bounded by:

Incident time window
Payment method
Bank
Maximum retry count
Maximum transaction amount
Explicit safety decisions
Audit logging

The current executor is simulated.

A production implementation would require:

Human approval for high-risk recovery
Idempotency guarantees
Payment-provider APIs
Authentication and authorization
Rate limiting
Distributed locks
Transaction-level audit infrastructure
Production observability
Rollback mechanisms
Compliance controls


📐 Evaluation Framework

RazorMind separates evaluation into multiple layers.

Detection
Precision
Recall
F1
Confusion matrix
Detection hit rate
Detection delay
Diagnosis
Root-cause accuracy
Component accuracy
Evidence consistency
Retrieval
Retrieval hit rate
Mean Reciprocal Rank
LLM
Structured-output validity
Grounding
Root-cause consistency
Recovery
Revenue at risk
Eligible revenue
Revenue recovered
Remaining risk
Revenue recovery rate
Transaction recovery rate
Eligible revenue recovery rate

This makes the system measurable from detection all the way through financial recovery.


🔮 Future Work

Potential production extensions include:

Real-time payment event streaming
Production payment-gateway integrations
Advanced anomaly detection
Learned root-cause models
Hybrid dense + lexical retrieval
Historical incident similarity
Incident timelines
Human-in-the-loop recovery approval
Multi-incident correlation
Distributed observability
Production monitoring and alerting


🏆 Built for Razorpay AI Buildathon 2026

RazorMind focuses on the intersection of:

AI
+
Payment Reliability
+
Incident Intelligence
+
Root Cause Analysis
+
Financial Impact
+
Safe Automation

The project demonstrates an AI system that does more than generate an explanation.

It connects:

Detection → Diagnosis → Financial Impact → Recovery → Evaluation → Explanation

while keeping automated financial actions bounded, auditable, and simulated.


👩‍💻 Author

Vijeta Vadehi Bandha

AI & ML Engineering

Built for Razorpay AI Buildathon 2026


