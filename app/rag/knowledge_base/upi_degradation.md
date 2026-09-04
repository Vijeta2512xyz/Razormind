# UPI Degradation Runbook

Use this runbook when UPI success rate falls while card and other payment methods remain comparatively healthy. Check UPI gateway health, upstream response codes, timeout rate, retry rate, and regional concentration. Compare UPI metrics against the recent baseline. If the degradation is isolated to UPI, escalate to the UPI gateway or upstream provider and avoid blaming an individual bank unless bank-specific evidence is present. Preserve timestamps, error codes, and affected regions for the incident record.
