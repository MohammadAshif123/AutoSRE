from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .kubernetes.client import KubernetesManager
from .memory.incident_memory import IncidentMemory
from .agents.observer import ObserverAgent
from .agents.diagnoser import DiagnoserAgent
from .agents.governor import GovernorAgent
from .agents.executor import ExecutorAgent
from .agents.orchestrator import Orchestrator
from .models.schemas import ActionRequest

app=FastAPI(title="AutoSRE MVP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

k8s=KubernetesManager(settings.k8s_namespace)
memory=IncidentMemory(settings.chroma_path)
observer=ObserverAgent(k8s)
diagnoser=DiagnoserAgent(k8s,memory)
governor=GovernorAgent()
executor=ExecutorAgent(k8s,settings.safe_mode)
orchestrator=Orchestrator(observer,diagnoser,governor,executor,memory)
incidents=[]

@app.get("/health")
def health(): return {"status":"ok","safe_mode":settings.safe_mode,"namespace":settings.k8s_namespace}

@app.get("/cluster/status")
def cluster_status():
    pods=k8s.list_pods()
    deployments=k8s.list_deployments()
    return {"namespace":settings.k8s_namespace,
            "pods":{"total":len(pods),"ready":sum(1 for p in pods if p.status.phase=="Running")},
            "deployments":[{"name":d.metadata.name,"ready":d.status.available_replicas or 0,"desired":d.spec.replicas} for d in deployments]}

@app.get("/services")
def services():
    return [{"name":x,"dependencies":{"frontend":["payment-service"],"payment-service":["database"],"database":[]}[x]} for x in ["frontend","payment-service","database"]]

@app.get("/incidents")
def get_incidents(): return incidents[-50:][::-1]

@app.get("/incidents/{incident_id}")
def get_incident(incident_id):
    for i in incidents:
        if i["id"]==incident_id:return i
    raise HTTPException(404,"Incident not found")

@app.post("/incidents/analyze")
def analyze():
    obs=observer.observe()
    out=[]
    for raw in obs:
        result=orchestrator.process(raw, execute=True)
        incidents.append(result); out.append(result)
    return out

@app.post("/actions/restart")
def restart(req:ActionRequest):
    if req.service not in executor.DEPLOYMENTS: raise HTTPException(400,"Service not allowed")
    inc={"id":"MANUAL","timestamp":"","service":req.service,"namespace":settings.k8s_namespace,
         "symptom":"Manual recovery request","evidence":[],"recommended_action":"restart"}
    result=executor.execute(inc); incidents.append(result); return result

@app.post("/actions/scale")
def scale(req:ActionRequest):
    if req.service not in executor.DEPLOYMENTS: raise HTTPException(400,"Service not allowed")
    inc={"id":"MANUAL","timestamp":"","service":req.service,"namespace":settings.k8s_namespace,
         "symptom":"Manual scale request","evidence":[],"recommended_action":"scale","replicas":req.replicas or 2}
    result=executor.execute(inc); incidents.append(result); return result

@app.post("/actions/rollback")
def rollback(req:ActionRequest):
    return {"status":"blocked","reason":"Rollback is intentionally disabled in this MVP until revision-safe validation is added."}

@app.post("/simulate/failure")
def simulate_failure(body:dict):
    if body.get("type")!="crash": raise HTTPException(400,"MVP supports type=crash")
    try:
        # Replaces the payment deployment command with a deterministic crash command.
        patch={"spec":{"template":{"spec":{"containers":[{"name":"payment","command":["/bin/sh","-c","echo 'AutoSRE demo crash'; exit 1"]}]}}}}
        k8s.apps.patch_namespaced_deployment("payment-service",settings.k8s_namespace,patch)
        return {"status":"triggered","type":"crash"}
    except Exception as e: raise HTTPException(500,str(e))

@app.post("/query")
def query(body:dict):
    q=(body.get("question") or "").lower()
    latest=incidents[-1] if incidents else None
    if not latest: return {"answer":"No incident has been observed yet. Trigger a failure and run analysis."}
    if "why" in q or "fail" in q:
        return {"answer":latest}
    return {"answer":"Ask about the latest incident, for example: Why did payment-service fail?"}
