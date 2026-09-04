from __future__ import annotations
from typing import Iterable
import pandas as pd

def binary_classification_metrics(y_true: Iterable[bool], y_pred: Iterable[bool]) -> dict:
    true = list(y_true); pred = list(y_pred)
    if len(true) != len(pred): raise ValueError("y_true and y_pred must have equal length")
    tp = sum(a and b for a,b in zip(true,pred)); tn=sum((not a) and (not b) for a,b in zip(true,pred))
    fp=sum((not a) and b for a,b in zip(true,pred)); fn=sum(a and (not b) for a,b in zip(true,pred))
    precision = tp/(tp+fp) if tp+fp else 0.0; recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"true_positive":tp,"true_negative":tn,"false_positive":fp,"false_negative":fn,"precision":precision,"recall":recall,"f1":f1}

def evaluate_detection(metrics: pd.DataFrame, incident_windows: list[tuple[str,str]]) -> dict:
    if "timestamp" not in metrics or "is_anomaly" not in metrics: raise ValueError("metrics must contain timestamp and is_anomaly")
    ts=pd.to_datetime(metrics["timestamp"])
    truth=pd.Series(False,index=metrics.index)
    for start,end in incident_windows: truth |= (ts>=pd.Timestamp(start)) & (ts<=pd.Timestamp(end))
    out=binary_classification_metrics(truth.tolist(), metrics["is_anomaly"].astype(bool).tolist())
    detections=ts[truth & metrics["is_anomaly"].astype(bool)]
    starts=[pd.Timestamp(s) for s,_ in incident_windows]
    delays=[]
    for start in starts:
        hits=detections[detections>=start]
        if len(hits): delays.append((hits.iloc[0]-start).total_seconds())
    out["detected_incidents"] = sum(any(d>=s for d in detections) for s in starts)
    out["total_incidents"] = len(starts)
    out["mean_detection_delay_seconds"] = sum(delays)/len(delays) if delays else None
    return out
