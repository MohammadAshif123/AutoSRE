from app.agents.governor import GovernorAgent

def test_high_confidence_restart_autoruns():
    x={"recommended_action":"restart","diagnosis_confidence":.95,
       "evidence":[{"message":"a"},{"message":"b"},{"message":"c"}],"similar_incidents":[]}
    y=GovernorAgent().evaluate(x)
    assert y["decision"]=="AUTO EXECUTE"
    assert 0 <= y["governor_confidence"] <= 1

def test_low_confidence_escalates():
    x={"recommended_action":None,"diagnosis_confidence":.2,"evidence":[],"similar_incidents":[]}
    assert GovernorAgent().evaluate(x)["decision"]=="ESCALATE"
