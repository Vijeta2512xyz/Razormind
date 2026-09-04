# Payment Gateway Failure Runbook

Use this runbook when gateway or upstream HTTP 5xx errors increase across payment traffic. Examine HTTP 500, 502, 503, and 504 responses, gateway error codes, failure rate, timeout rate, and retry volume. If multiple payment methods or banks are affected at the same time, prioritize the shared payment gateway or upstream provider as the root-cause candidate.
