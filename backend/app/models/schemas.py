from pydantic import BaseModel, Field
from typing import Any, Optional

class Evidence(BaseModel):
    source: str
    message: str

class Incident(BaseModel):
    id: str
    timestamp: str
    service: str
    namespace: str
    symptom: str
    status: str = "active"
    evidence: list[Evidence] = []
    root_cause: Optional[str] = None
    recommended_action: Optional[str] = None
    diagnosis_confidence: float = 0.0
    governor_confidence: float = 0.0
    decision: Optional[str] = None
    risk: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    recovery_succeeded: Optional[bool] = None
    similar_incidents: list[dict[str, Any]] = []
    dependencies: dict[str, list[str]] = {}

class ActionRequest(BaseModel):
    service: str
    replicas: Optional[int] = Field(default=None, ge=1, le=5)
    incident_id: Optional[str] = None
