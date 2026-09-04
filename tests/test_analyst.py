import json
import pytest
from app.llm.analyst import AnalystInput, build_prompt, validate_report, analyze
D={'incident_id':'INC-001','leading_hypothesis':'bank:hdfc','evidence':{'failure_rate':.65,'baseline_failure_rate':.02},'affected_components':['bank:hdfc']}
R=[{'document':'bank_failure.md','score':.81,'text':'Check bank upstream health and route traffic.'}]
def good(): return {'summary':'HDFC failures increased sharply.','severity':'high','likely_root_cause':'bank:hdfc','affected_components':['bank:hdfc'],'evidence':['failure_rate=0.65'],'recommended_actions':['Check HDFC upstream health'],'confidence':.93}
def test_prompt_grounded():
 p=build_prompt(AnalystInput(D,R)); assert 'bank:hdfc' in p and 'bank_failure.md' in p and 'Do not invent metrics' in p
def test_valid(): assert validate_report(good())['severity']=='high'
def test_missing():
 x=good(); del x['evidence']
 with pytest.raises(ValueError): validate_report(x)
def test_bad_severity():
 x=good(); x['severity']='urgent'
 with pytest.raises(ValueError): validate_report(x)
def test_bad_confidence():
 x=good(); x['confidence']=1.5
 with pytest.raises(ValueError): validate_report(x)
def test_analyze_mock():
 x=good(); seen={}
 def fake(p): seen['p']=p; return json.dumps(x)
 assert analyze(D,R,fake)==x and 'failure_rate' in seen['p']
def test_invalid_json():
 with pytest.raises(ValueError,match='invalid JSON'): analyze(D,R,lambda _: 'not json')
