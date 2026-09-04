# RazorMind — AI-Powered Payment Reliability & Incident Intelligence

RazorMind is an AI-powered payment reliability system that detects payment incidents, diagnoses likely root causes, quantifies revenue at risk, executes bounded recovery actions, measures recovered revenue, and generates grounded incident reports.

It is designed around one principle:

> **The LLM explains the incident — it does not decide whether an incident exists.**

---

## 🚀 What RazorMind Does

RazorMind closes the loop from payment failure to measurable recovery:

```text
Payment Transactions
        ↓
Incident Simulation
        ↓
Statistical Detection
        ↓
Incident Diagnosis / RCA
        ↓
Revenue at Risk
        ↓
Recovery Strategy
        ↓
Safety Checks
        ↓
Bounded Recovery Execution
        ↓
Recovery Evaluation
        ↓
RAG + LLM Incident Report
🧠 Architecture
                    ┌─────────────────────┐
                    │ Payment Simulator   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Incident Injector   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Metrics Aggregation │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Anomaly Detection   │
                    │ Rolling Baseline    │
                    │ Z-Score / EWMA      │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Incident Diagnosis  │
                    │ Evidence + RCA      │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Revenue Risk        │
                    │ Quantification      │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Recovery Strategy   │
                    │ Safety Constraints  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Bounded Recovery    │
                    │ Simulation          │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Recovery Evaluation │
                    └──────────┬──────────┘
                               ↓
              ┌────────────────┴────────────────┐
              ↓                                 ↓
      ┌─────────────────┐              ┌─────────────────┐
      │ RAG Runbooks    │              │ LLM Analyst     │
      └─────────────────┘              └─────────────────┘
                       \                /
                        \              /
                         ↓            ↓
                    Incident Report
🔍 Incident Detection

RazorMind does not rely on an LLM to detect anomalies.

The detection layer operates on transaction-derived metrics and statistical baselines.

It monitors signals including:

Payment failure rate
Latency
Timeout rate
Retry behavior
Payment method performance
Bank performance
Regional degradation

The detection layer produces structured incident candidates that are passed to diagnosis.

🧩 Root-Cause Diagnosis

The diagnosis layer compares incident-window behavior against baseline behavior.

It evaluates multiple hypotheses such as:

Bank degradation
Payment-method degradation
Gateway failure
Regional degradation
Latency spike
Timeout spike

The leading hypothesis is selected deterministically from the evidence.

For example:

Incident: INC-UPI-001

Leading hypothesis:
payment_method:upi

Reason:
Payment method upi has the highest failure-rate lift
versus the incident window overall.

This deterministic diagnosis becomes authoritative input to the LLM.

📚 RAG Runbook Retrieval

RazorMind includes a lightweight retrieval layer over operational runbooks.

Example knowledge-base documents include:

bank_failure.md
gateway_failure.md
latency_spike.md
regional_degradation.md
timeout_spike.md
upi_degradation.md

The retriever uses vector-style similarity to identify runbooks relevant to the diagnosed incident.

The retrieved operational knowledge is then supplied to the incident analyst.

💰 Revenue-at-Risk Quantification

RazorMind connects technical incidents to business impact.

For a detected incident, the system calculates:

Revenue at Risk
        ↓
Eligible Recovery Revenue
        ↓
Revenue Recovered
        ↓
Remaining Revenue Risk

This makes the incident measurable from both an engineering and financial perspective.

⚙️ Bounded Recovery

RazorMind does not blindly retry every failed transaction.

Every candidate transaction must pass deterministic safety constraints.

Examples:

Transaction must fall inside the incident window
Transaction must have failed
Transaction must belong to the affected payment method/bank
Retry count must remain below the configured maximum
Transaction amount must remain below the configured maximum

Each candidate produces an audit record.

Failed Transaction
       ↓
Safety Rules
   ↙       ↘
PASS       REJECT
 ↓           ↓
Retry       Stop

The recovery executor is intentionally a simulation and does not call a real payment provider.

📊 Recovery Evaluation

After bounded recovery execution, RazorMind measures:

Revenue recovered
Remaining revenue risk
Revenue recovery rate
Eligible recovery rate
Transaction recovery rate
Number of recovered transactions
Number of rejected transactions

This creates a measurable before/after recovery view.

🤖 Grounded LLM Incident Analyst

The LLM is used for explanation rather than detection.

The analyst receives:

Deterministic Diagnosis
        +
Retrieved Runbooks
        +
Actual Recovery Outcome
        ↓
Grounded Incident Report

The report contains:

Summary
Severity
Likely root cause
Affected components
Evidence
Recommended actions
Confidence

The system explicitly prevents the LLM from replacing the deterministic root-cause diagnosis or inventing recovery outcomes.

🧪 Example Incident
INC-UPI-001

A simulated UPI degradation was injected into the transaction stream.

Incident type:
upi_degradation

Severity:
high

Affected component:
payment_method:upi
Financial impact
Revenue at risk:
₹437,676.16

Eligible recovery revenue:
₹275,283.98

Revenue recovered:
₹202,829.76

Remaining risk:
₹234,846.40
Recovery
Strategy:
bounded_retry

Recovered transactions:
149

Failed transactions in incident:
350

The final report is generated from the actual deterministic recovery outcome rather than hypothetical LLM-generated values.

🛡️ Safety by Design

RazorMind treats automated recovery as a bounded decision problem.

The system includes:

Maximum retry limits
Maximum transaction amount
Incident-window restrictions
Payment-method/bank restrictions
Candidate-level safety decisions
Audit trail
Deterministic recovery evaluation
Simulated execution instead of real payment execution

This allows recovery logic to be evaluated without interacting with real financial infrastructure.

📈 Evaluation

RazorMind includes automated evaluation for multiple layers of the system.

Detection
Precision
Recall
F1
Confusion counts
Incident hit rate
Detection delay
Diagnosis
Root-cause accuracy
Component accuracy
RAG
Hit rate
Mean Reciprocal Rank (MRR)
LLM
Structured-output validity
Basic grounding checks
Recovery
Revenue recovered
Remaining risk
Revenue recovery rate
Transaction recovery rate
Eligible recovery rate
🧪 Testing

The project currently contains 86 automated tests covering:

Transaction generation
Incident injection
Metrics
Detection
Diagnosis
RAG
LLM analyst
Evaluation
Revenue-risk calculation
Recovery strategy
Recovery execution
Recovery evaluation
End-to-end recovery pipeline
Dashboard behavior

Run the complete test suite:

pytest -q

Expected result:

86 passed
🖥️ Dashboard

RazorMind includes a Streamlit dashboard for interactive incident analysis.

The dashboard provides:

Incident selection
Detection results
Root-cause diagnosis
Evidence
Retrieved runbooks
Revenue-at-risk analysis
Recovery strategy
Recovery execution results
Recovery evaluation
Grounded LLM incident report
🛠️ Tech Stack
Python
Pandas
NumPy
SQLite
Streamlit
Scikit-learn
TF-IDF / cosine similarity
Ollama
Pytest
📁 Project Structure
razormind/
│
├── app/
│   ├── simulator/
│   │   ├── generator.py
│   │   ├── incidents.py
│   │   └── schema.sql
│   │
│   ├── detection/
│   │   ├── metrics.py
│   │   ├── baseline.py
│   │   └── detector.py
│   │
│   ├── diagnosis/
│   │   ├── evidence.py
│   │   └── root_cause.py
│   │
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── knowledge_base/
│   │
│   ├── llm/
│   │   └── analyst.py
│   │
│   ├── recovery/
│   │   ├── revenue.py
│   │   ├── strategy.py
│   │   ├── executor.py
│   │   ├── evaluator.py
│   │   └── pipeline.py
│   │
│   ├── evaluation/
│   │   ├── detection_metrics.py
│   │   ├── diagnosis_metrics.py
│   │   └── evaluation_runner.py
│   │
│   └── dashboard.py
│
├── data/
├── notebooks/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
▶️ Running RazorMind

Clone the repository and enter the project directory:

git clone https://github.com/Vijeta2512xyz/Razormind.git
cd Razormind

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the tests:

pytest -q

Launch the dashboard:

$env:PYTHONPATH=(Get-Location).Path
streamlit run app/dashboard.py

For local LLM reporting with Ollama:

$env:RAZORMIND_OLLAMA_MODEL="phi:latest"
streamlit run app/dashboard.py
🔐 Data & Safety

RazorMind uses simulated payment data.

No real payment transactions are executed.

The recovery executor is intentionally bounded and simulated for experimentation and evaluation.

Database files, environment variables, model artifacts, and other local-only files are excluded through .gitignore.

🎯 Design Philosophy

RazorMind follows a simple architecture:

Deterministic systems establish what happened. AI explains why it matters.

This separation makes the system more auditable, testable, and safer than using an LLM as the primary incident detector or recovery decision-maker.

🚀 Future Work

Potential extensions include:

Real-time streaming transaction ingestion
Production-grade vector databases
More advanced anomaly detection
Multi-gateway routing optimization
Human-in-the-loop recovery approval
Real payment-provider sandbox integration
Historical incident learning
Recovery-policy optimization
Production observability integration
👩‍💻 Author

Vijeta Vadehi Bandha

Built as an AI-powered payment reliability and incident intelligence project for the Razorpay AI Buildathon 2026.

