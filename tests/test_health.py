from fastapi.testclient import TestClient
# This imports the real app and therefore expects a valid local Kubernetes config.
# Use `pytest -q` after Minikube is running.
from app.main import app

def test_health():
    r=TestClient(app).get("/health")
    assert r.status_code==200
    assert r.json()["namespace"]=="autosre-demo"
