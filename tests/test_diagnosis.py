from app.agents.diagnoser import DiagnoserAgent

class DummyMemory:
    def similar(self,x): return []

def test_crashloop_rule():
    d=DiagnoserAgent(None,DummyMemory())
    x={"service":"payment-service","symptom":"CrashLoopBackOff","evidence":[{"message":"restart_count=5"}]}
    y=d.diagnose(x)
    assert y["recommended_action"]=="restart"
    assert y["diagnosis_confidence"]>.8
