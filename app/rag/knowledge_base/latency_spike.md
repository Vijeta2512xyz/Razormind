# Latency Spike Runbook

Use this runbook when p95 or mean payment latency rises across a broad portion of traffic. Compare latency by payment method, bank, and region. Check whether failure and timeout rates also rise. Investigate gateway queues, upstream latency, database saturation, and network conditions. A broad latency increase without a single isolated bank or method points toward shared infrastructure or gateway latency.
