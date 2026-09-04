# Timeout Spike Runbook

Use this runbook when TIMEOUT errors or HTTP 408/504 responses rise and retries increase. Compare timeout rate and p95 latency with baseline. Determine whether timeouts are isolated to a payment method, bank, region, or shared gateway. Check upstream response time and network health. Preserve the timeout and retry evidence when escalating.
