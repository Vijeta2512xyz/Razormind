from __future__ import annotations
from .detection_metrics import evaluate_detection
from .diagnosis_metrics import evaluate_diagnosis

def evaluate_rag(retrieval_cases: list[dict]) -> dict:
    if not retrieval_cases: return {"total":0,"hit_rate":0.0,"mean_reciprocal_rank":0.0}
    hits=0; rr=0.0
    for case in retrieval_cases:
        expected=set(case["relevant_document_ids"]); results=case["results"]
        rank=next((i+1 for i,r in enumerate(results) if r["document_id"] in expected),None)
        if rank: hits+=1; rr+=1/rank
    n=len(retrieval_cases)
    return {"total":n,"hit_rate":hits/n,"mean_reciprocal_rank":rr/n}

def evaluate_llm(reports: list[dict]) -> dict:
    required={"summary","severity","likely_root_cause","affected_components","evidence","recommended_actions","confidence"}
    valid=grounded=0
    for r in reports:
        valid += int(required.issubset(r) and r.get("severity") in {"low","medium","high","critical"} and isinstance(r.get("confidence"),(int,float)) and 0<=r["confidence"]<=1)
        grounded += int(bool(r.get("evidence")) and bool(r.get("likely_root_cause")))
    n=len(reports)
    return {"total":n,"valid_json_rate":valid/n if n else 0.0,"grounded_report_rate":grounded/n if n else 0.0}

def run_evaluation(*, detection_metrics=None, incident_windows=None, diagnoses=None, retrieval_cases=None, reports=None) -> dict:
    result={}
    if detection_metrics is not None: result["detection"]=evaluate_detection(detection_metrics, incident_windows or [])
    if diagnoses is not None: result["diagnosis"]=evaluate_diagnosis(diagnoses)
    if retrieval_cases is not None: result["rag"]=evaluate_rag(retrieval_cases)
    if reports is not None: result["llm"]=evaluate_llm(reports)
    return result
