# Bank Failure Runbook

Use this runbook when failures are concentrated on one bank while other banks continue near baseline. Compare the affected bank's failure rate, latency, timeout count, HTTP status distribution, and retry rate against unaffected banks. Verify whether the pattern is isolated to one payment method or appears across methods. If one bank is strongly isolated, escalate to that bank or its processor and include the measured failure-rate lift and timestamps in the incident record.
