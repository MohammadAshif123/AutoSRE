from app.agents.executor import ExecutorAgent

class DummyK8s: pass

def test_allowlist_and_safe_mode():
    e=ExecutorAgent(DummyK8s(),safe_mode=True)
    x={"id":"X","service":"payment-service","recommended_action":"restart"}
    y=e.execute(x)
    assert y["recovery_succeeded"] is False
    assert "SAFE_MODE" in y["result"]

def test_unknown_resource_blocked():
    e=ExecutorAgent(DummyK8s(),safe_mode=False)
    x={"id":"X","service":"prod-api","recommended_action":"restart"}
    y=e.execute(x)
    assert "allowlist" in y["result"]
