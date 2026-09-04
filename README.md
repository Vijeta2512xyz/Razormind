# **RAZORMIND**

## 

## \## AI-POWERED PAYMENT RELIABILITY \& INCIDENT INTELLIGENCE SYSTEM



RazorMind is an AI-powered payment reliability and incident intelligence platform designed to detect payment failures, diagnose root causes, estimate financial impact, execute bounded recovery strategies, and generate grounded incident reports.



The system combines statistical anomaly detection, deterministic root-cause analysis, Retrieval-Augmented Generation (RAG), bounded recovery automation, and LLM-based incident analysis into a single end-to-end workflow.



\---



### **1. PROJECT OVERVIEW**



#### \## 1.1 Problem Statement



Payment systems can experience sudden increases in:



\- Payment failures

\- Transaction latency

\- Timeouts

\- Retries

\- Processor errors

\- Bank-specific failures

\- Payment-method-specific failures



Traditional monitoring systems can identify that something is wrong, but engineers often need to manually investigate the incident and determine:



1\. What failed?

2\. Which payment method or component is affected?

3\. What is the likely root cause?

4\. How much revenue is at risk?

5\. Which recovery strategy should be applied?

6\. How much revenue can be recovered?

7\. What actions should the incident-response team take?



RazorMind automates this workflow from detection through recovery and post-incident analysis.



\---



### **2. END-TO-END WORKFLOW**



```text

PAYMENT SIMULATOR

&#x20;       |

&#x20;       v

INCIDENT INJECTION

&#x20;       |

&#x20;       v

METRICS AGGREGATION

&#x20;       |

&#x20;       v

ANOMALY DETECTION

&#x20;       |

&#x20;       v

INCIDENT CORRELATION

&#x20;       |

&#x20;       v

ROOT-CAUSE DIAGNOSIS

&#x20;       |

&#x20;       v

REVENUE AT RISK

&#x20;       |

&#x20;       v

RECOVERY STRATEGY

&#x20;       |

&#x20;       v

BOUNDED RECOVERY EXECUTION

&#x20;       |

&#x20;       v

RECOVERY EVALUATION

&#x20;       |

&#x20;       v

RAG RUNBOOK RETRIEVAL

&#x20;       |

&#x20;       v

GROUNDED LLM INCIDENT REPORT



### **3. SYSTEM ARCHITECTURE**

&#x20;                        RAZORMIND

&#x20;                            |

&#x20;             +--------------+--------------+

&#x20;             |                             |

&#x20;             v                             v

&#x20;     PAYMENT SIMULATOR              INCIDENT INJECTOR

&#x20;             |                             |

&#x20;             +--------------+--------------+

&#x20;                            |

&#x20;                            v

&#x20;                    METRICS ENGINE

&#x20;                            |

&#x20;                            v

&#x20;                   ANOMALY DETECTOR

&#x20;                            |

&#x20;                            v

&#x20;                  INCIDENT CORRELATOR

&#x20;                            |

&#x20;                            v

&#x20;                   ROOT-CAUSE ENGINE

&#x20;                            |

&#x20;               +------------+------------+

&#x20;               |                         |

&#x20;               v                         v

&#x20;         REVENUE RISK               RAG RETRIEVER

&#x20;               |                         |

&#x20;               v                         v

&#x20;       RECOVERY ENGINE             RUNBOOK CONTEXT

&#x20;               |                         |

&#x20;               +------------+------------+

&#x20;                            |

&#x20;                            v

&#x20;                      LLM ANALYST

&#x20;                            |

&#x20;                            v

&#x20;                   STREAMLIT DASHBOARD





### **4. PAYMENT SIMULATION**



RazorMind begins with a configurable payment transaction simulator.



The simulator generates transaction-level data containing information such as:



Transaction ID

Timestamp

Payment method

Bank

Transaction amount

Transaction status

Latency

Retry count



The generated data provides a controlled environment for testing incident detection and recovery.



### **5. INCIDENT INJECTION**



The incident injector creates realistic payment incidents on top of the simulated transaction data.



Supported incident behavior includes conditions such as:



Increased failure rate

Increased latency

Increased timeout rate

Increased retries

Payment-method degradation

Bank-specific degradation



Each incident contains structured metadata such as:



Incident ID

Incident Type

Start Time

End Time

Severity

Affected Component

Affected Payment Method

Expected Symptoms



This allows the detection and diagnosis systems to be evaluated against known ground truth.



### **6. METRICS \& MONITORING**



RazorMind aggregates transaction-level data into operational payment metrics.



The monitoring layer tracks:



Transaction volume

Success rate

Failure rate

Mean latency

P95 latency

Retry rate

Timeout rate

Payment-method performance

Bank performance



These metrics form the input to the anomaly-detection pipeline.



### **7. ANOMALY DETECTION**



RazorMind does not use an LLM as the primary incident detector.



Detection is based on structured payment metrics and statistical signals.



The detection layer supports techniques such as:



Rolling baselines

Z-score based anomaly detection

EWMA-style monitoring



The detector identifies abnormal behavior while keeping the detection process deterministic and reproducible.



### **8. INCIDENT CORRELATION**



Multiple anomalous signals may appear simultaneously during a payment incident.



RazorMind correlates these signals to determine whether they belong to the same incident.



The correlation layer considers:



Time windows

Payment methods

Banks

Failure behavior

Latency behavior

Timeout behavior

Retry behavior



This produces a structured incident representation for downstream diagnosis.



### **9. ROOT-CAUSE DIAGNOSIS**



After detecting an incident, RazorMind extracts structured evidence from the affected incident window.



The diagnosis engine evaluates multiple root-cause dimensions:



Payment method

Bank

Processor

Failure rate

Timeout rate

Latency

Retry behavior



Root-cause candidates are scored using observed evidence rather than generated explanations.



For example:



Leading Root Cause:

payment\_method:upi



This allows the LLM to explain the diagnosis instead of inventing the diagnosis.



### **10. RETRIEVAL-AUGMENTED GENERATION**



RazorMind includes a lightweight Retrieval-Augmented Generation pipeline for incident-response knowledge.



#### 10.1 RAG Pipeline

RUNBOOKS

&#x20;   |

&#x20;   v

DOCUMENT PROCESSING

&#x20;   |

&#x20;   v

SEARCHABLE REPRESENTATION

&#x20;   |

&#x20;   v

SIMILARITY RETRIEVAL

&#x20;   |

&#x20;   v

RELEVANT RUNBOOKS

&#x20;   |

&#x20;   v

LLM INCIDENT ANALYSIS



#### 10.2 Retrieval



The retrieval system searches the incident knowledge base and returns runbooks relevant to the diagnosed incident.



Example runbook categories include:



UPI degradation

Bank failures

Processor failures

Payment gateway issues

Increased latency

Elevated timeout rates



The retrieved information provides operational context for the final incident analysis.



### **11. REVENUE AT RISK**



RazorMind goes beyond detecting technical failures.



It estimates the financial impact of an incident.



Revenue at risk is calculated from failed transactions inside the affected incident window.



REVENUE AT RISK

=

SUM OF FAILED TRANSACTION AMOUNTS



The calculation can be restricted to:



Affected payment method

Affected bank

Incident time window



This converts an operational incident into a measurable business-impact signal.



### **12. RECOVERY STRATEGY**



RazorMind determines which failed transactions are eligible for bounded recovery.



The strategy layer applies explicit safety rules before a transaction can be retried.



FAILED TRANSACTION

&#x20;       |

&#x20;       v

SAFETY CHECKS

&#x20;       |

&#x20;       +---- RETRY LIMIT EXCEEDED ----> REJECT

&#x20;       |

&#x20;       +---- AMOUNT LIMIT EXCEEDED ---> REJECT

&#x20;       |

&#x20;       v

BOUNDED RETRY



Safety constraints include:



Incident-window filtering

Payment-method filtering

Bank filtering

Maximum retry count

Maximum transaction amount



Each candidate transaction receives an audit record explaining whether it was approved or rejected.

### 

### **13. BOUNDED RECOVERY EXECUTION**



Approved transactions are passed to the recovery executor.



Recovery is intentionally simulated and bounded.



The executor:



Receives eligible transactions.

Performs one simulated recovery attempt per transaction.

Uses a configurable recovery probability.

Produces recovered transaction and revenue totals.

Records the recovery outcome.



The system does not call a real payment provider or perform unrestricted financial transactions.



### **14. RECOVERY EVALUATION**



After execution, RazorMind evaluates the recovery outcome.



The evaluation layer calculates:



Revenue recovered

Remaining revenue at risk

Revenue recovery rate

Eligible recovery rate

Transaction recovery rate

Number of recovered transactions

Number of failed transactions



This creates a measurable before-and-after view of the incident.



### **15. LLM INCIDENT ANALYST**



The LLM operates as an explanation and reasoning layer.



It receives structured information including:



Incident diagnosis

Root-cause evidence

Retrieved runbooks

Revenue-at-risk information

Recovery strategy

Recovery outcome



The LLM generates a structured incident report containing:



Incident summary

Severity

Likely root cause

Affected components

Supporting evidence

Recommended actions

Confidence



The system is designed so that the LLM does not independently determine the primary incident.



### **16. EXAMPLE INCIDENT**

#### 16.1 Incident Details

Incident ID: INC-UPI-001

Incident Type: UPI Degradation

Severity: High

Affected Component: UPI

Incident Window: 01:00 - 01:30

### 16.2 Diagnosis

Leading Root Cause:

payment\_method:upi

### 16.3 Financial Impact

Revenue At Risk:       INR 437,676.16

Eligible Revenue:      INR 275,283.98

Revenue Recovered:     INR 202,829.76

Remaining Risk:        INR 234,846.40

### 16.4 Transaction Impact

Failed Transactions:   350

Recovered Transactions: 149

### 16.5 Recovery Configuration

Strategy:

bounded\_retry



Maximum Retries:

2



Maximum Transaction Amount:

INR 10,000





### **17. SAFETY \& CONTROL**



RazorMind follows a bounded automation approach.



The recovery system does not automatically perform unrestricted financial actions.



Recovery is constrained by:



INCIDENT WINDOW

AFFECTED PAYMENT METHOD

AFFECTED BANK

MAXIMUM RETRIES

MAXIMUM TRANSACTION AMOUNT

AUDIT TRAIL



Each recovery candidate is explicitly classified as:



APPROVED



or:



REJECTED



with a corresponding reason.



This provides traceability and makes the recovery process auditable.



### **18. EVALUATION FRAMEWORK**



RazorMind includes automated evaluation across the major pipeline components.



#### 18.1 Detection Evaluation



Metrics include:



Precision

Recall

F1 Score

Confusion counts

Incident hit rate

Detection delay



#### 18.2 Diagnosis Evaluation



Metrics include:



Root-cause accuracy

Component accuracy



#### 18.3 RAG Evaluation



Metrics include:



Retrieval hit rate

Mean Reciprocal Rank



#### 18.4 LLM Evaluation



Metrics include:



Structured-output validity

Basic grounding checks



#### 18.5 Recovery Evaluation



Metrics include:



Revenue recovered

Remaining revenue risk

Revenue recovery rate

Transaction recovery rate





### **19. STREAMLIT DASHBOARD**



RazorMind includes an interactive Streamlit dashboard for incident investigation.



The dashboard provides visibility into:



Incident details

Detection results

Root-cause diagnosis

Evidence

Revenue at risk

Recovery strategy

Recovery results

Before-and-after impact

Retrieved runbooks

LLM incident analysis





### **20. TESTING**



The project includes automated tests covering the major components of the system.



Current test suite:



86 TESTS PASSED



Run the complete test suite:



python -m pytest -q





### **21. TECHNOLOGY STACK**

#### 21.1 Programming \& Data

Python

Pandas

NumPy

SQLite

#### 21.2 Machine Learning \& Retrieval

Scikit-learn

TF-IDF retrieval

Cosine similarity

Statistical anomaly detection

#### 21.3 Generative AI

Ollama

Local LLM inference

Retrieval-Augmented Generation

#### 21.4 Dashboard

Streamlit

#### 21.5 Testing

Pytest



### **22. PROJECT STRUCTURE**

razormind/

|

+-- app/

|   |

|   +-- simulator/

|   |   +-- generator.py

|   |   +-- incidents.py

|   |   +-- schema.sql

|   |

|   +-- detection/

|   |   +-- metrics.py

|   |   +-- baseline.py

|   |   +-- detector.py

|   |

|   +-- diagnosis/

|   |   +-- evidence.py

|   |   +-- root\_cause.py

|   |

|   +-- rag/

|   |   +-- ingest.py

|   |   +-- retriever.py

|   |   +-- knowledge\_base/

|   |

|   +-- llm/

|   |   +-- analyst.py

|   |

|   +-- evaluation/

|   |   +-- detection\_metrics.py

|   |   +-- diagnosis\_metrics.py

|   |   +-- evaluation\_runner.py

|   |

|   +-- recovery/

|       +-- revenue.py

|       +-- strategy.py

|       +-- executor.py

|       +-- evaluator.py

|       +-- pipeline.py

|

+-- data/

|   +-- raw/

|   +-- processed/

|

+-- models/

|

+-- notebooks/

|

+-- tests/

|   +-- test\_generator.py

|   +-- test\_incidents.py

|   +-- test\_detection.py

|   +-- test\_diagnosis.py

|

+-- requirements.txt

+-- README.md

+-- .gitignore





### **23. RUNNING THE PROJECT**

#### 23.1 Clone the Repository

git clone https://github.com/Vijeta2512xyz/Razormind.git

cd Razormind

#### 23.2 Install Dependencies

pip install -r requirements.txt

#### 23.3 Run Tests

python -m pytest -q

#### 23.4 Run the Dashboard

streamlit run app/dashboard.py

#### 23.5 Run with Local Ollama Model

$env:PYTHONPATH=(Get-Location).Path

$env:RAZORMIND\_OLLAMA\_MODEL="phi:latest"

streamlit run app/dashboard.py





### **24. DESIGN PHILOSOPHY**



The central design principle of RazorMind is:



LLM FOR REASONING AND EXPLANATION



NOT



LLM FOR BASIC MONITORING



The system separates deterministic operational logic from generative AI.



RAW TRANSACTION DATA

&#x20;       |

&#x20;       v

DETERMINISTIC METRICS

&#x20;       |

&#x20;       v

STATISTICAL DETECTION

&#x20;       |

&#x20;       v

STRUCTURED DIAGNOSIS

&#x20;       |

&#x20;       v

REVENUE IMPACT

&#x20;       |

&#x20;       v

BOUNDED RECOVERY

&#x20;       |

&#x20;       v

RAG CONTEXT

&#x20;       |

&#x20;       v

LLM EXPLANATION



This architecture improves:



Reliability

Reproducibility

Explainability

Testability

Grounding

Safety





### **25. FUTURE WORK**



Potential future improvements include:



Real-time payment event streaming

Production payment gateway integrations

More advanced anomaly detection

Learned root-cause ranking

Hybrid sparse and dense retrieval

Historical incident similarity search

Automated incident timelines

Human approval workflows for recovery

Multi-incident correlation

Distributed observability integration

Production-grade monitoring and alerting





### **26. BUILDATHON**



RazorMind was developed for the:



RAZORPAY AI BUILDATHON 2026



The project focuses on applying AI to:



Payment reliability

Incident intelligence

Root-cause diagnosis

Financial impact analysis

Retrieval-Augmented Generation

Bounded operational recovery





### **27. AUTHOR**



VIJETA VADEHI BANDHA



AI \& MACHINE LEARNING ENGINEERING



RAZORMIND



Razorpay AI Buildathon 2026

