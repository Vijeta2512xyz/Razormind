import pandas as pd
import pytest
from app.evaluation.detection_metrics import binary_classification_metrics, evaluate_detection
from app.evaluation.diagnosis_metrics import evaluate_diagnosis
from app.evaluation.evaluation_runner import evaluate_rag, evaluate_llm, run_evaluation

def test_binary_metrics_perfect():
    m=binary_classification_metrics([1,1,0,0],[1,1,0,0]); assert m["f1"]==1 and m["precision"]==1

def test_binary_metrics_confusion_counts():
    m=binary_classification_metrics([1,1,0,0],[1,0,1,0]); assert (m["true_positive"],m["false_negative"],m["false_positive"],m["true_negative"])==(1,1,1,1)

def test_binary_length_validation():
    with pytest.raises(ValueError): binary_classification_metrics([1],[1,0])

def test_detection_window_metrics():
    df=pd.DataFrame({"timestamp":pd.date_range("2026-01-01 10:00",periods=6,freq="min"),"is_anomaly":[False,False,True,True,False,False]})
    r=evaluate_detection(df,[("2026-01-01 10:02","2026-01-01 10:03")]); assert r["recall"]==1 and r["detected_incidents"]==1 and r["mean_detection_delay_seconds"]==0

def test_detection_no_incident_hit():
    df=pd.DataFrame({"timestamp":pd.date_range("2026-01-01 10:00",periods=3,freq="min"),"is_anomaly":[False,False,True]})
    r=evaluate_detection(df,[("2026-01-01 10:00","2026-01-01 10:01")]); assert r["detected_incidents"]==0

def test_diagnosis_accuracy():
    d={"ground_truth":{"incident_type":"bank_failure","affected_bank":"hdfc","affected_component":"bank:hdfc"},"leading_hypothesis":{"root_cause_type":"bank_failure","component":"bank:hdfc"}}
    r=evaluate_diagnosis([d]); assert r["root_cause_accuracy"]==1 and r["component_accuracy"]==1

def test_diagnosis_empty(): assert evaluate_diagnosis([])["total"]==0

def test_rag_hit_and_rank():
    r=evaluate_rag([{"relevant_document_ids":["upi"],"results":[{"document_id":"gateway"},{"document_id":"upi"}]}]); assert r["hit_rate"]==1 and r["mean_reciprocal_rank"]==0.5

def test_rag_empty(): assert evaluate_rag([])["hit_rate"]==0

def test_llm_quality():
    r=evaluate_llm([{"summary":"x","severity":"high","likely_root_cause":"bank:hdfc","affected_components":["bank:hdfc"],"evidence":["failure rate increased"],"recommended_actions":["check bank"],"confidence":0.9}]); assert r["valid_json_rate"]==1 and r["grounded_report_rate"]==1

def test_llm_invalid(): assert evaluate_llm([{"severity":"bad"}])["valid_json_rate"]==0

def test_runner_combines_metrics():
    out=run_evaluation(diagnoses=[], retrieval_cases=[], reports=[]); assert set(out)=={"diagnosis","rag","llm"}
