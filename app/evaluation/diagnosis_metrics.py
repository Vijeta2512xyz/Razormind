from __future__ import annotations

def evaluate_diagnosis(diagnoses: list[dict]) -> dict:
    if not diagnoses: return {"total":0,"root_cause_accuracy":0.0,"component_accuracy":0.0}
    root=comp=0
    for d in diagnoses:
        truth=d.get("ground_truth",{}); hyp=d.get("leading_hypothesis",{})
        expected_type=truth.get("incident_type"); expected_component=truth.get("affected_component")
        actual_type=hyp.get("root_cause_type"); actual_component=hyp.get("component")
        root += int(actual_type == expected_type or (expected_type == "bank_failure" and actual_type == "bank_failure"))
        target=(f"bank:{truth.get('affected_bank')}" if truth.get('affected_bank') else
                f"payment_method:{truth.get('affected_payment_method')}" if truth.get('affected_payment_method') else
                f"region:{truth.get('affected_region')}" if truth.get('affected_region') else expected_component)
        comp += int(actual_component == target or actual_component == expected_component)
    return {"total":len(diagnoses),"root_cause_accuracy":root/len(diagnoses),"component_accuracy":comp/len(diagnoses)}
