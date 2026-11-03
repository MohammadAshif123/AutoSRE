import json, os
from datetime import datetime, timezone

class ExecutorAgent:
    ALLOWED={"restart","scale","rollback"}
    DEPLOYMENTS={"frontend","payment-service","database"}

    def __init__(self,k8s,safe_mode=True):
        self.k8s=k8s
        self.safe_mode=safe_mode
        self.audit_path="data/audit.log"
        os.makedirs("data",exist_ok=True)

    def _audit(self, event):
        with open(self.audit_path,"a",encoding="utf-8") as f:
            f.write(json.dumps({"timestamp":datetime.now(timezone.utc).isoformat(),**event})+"\n")

    def execute(self, incident):
        action=incident.get("recommended_action")
        service=incident.get("service")
        if action not in self.ALLOWED or service not in self.DEPLOYMENTS:
            incident.update({"result":"Blocked: action/resource not on allowlist.","recovery_succeeded":False})
            return incident
        if self.safe_mode:
            incident.update({"result":"SAFE_MODE blocked autonomous Kubernetes mutation. Approval required.","recovery_succeeded":False})
            self._audit({"incident_id":incident["id"],"action":action,"service":service,"result":"blocked_safe_mode"})
            return incident
        try:
            if action=="restart":
                pods=[p for p in self.k8s.list_pods() if (p.metadata.labels or {}).get("app")==service]
                if not pods: raise RuntimeError("No target pod found")
                for p in pods:
                    self.k8s.restart_pod(p.metadata.name)
                ok=self.k8s.deployment_ready(service)
            elif action=="scale":
                replicas=incident.get("replicas",2)
                self.k8s.scale_deployment(service,replicas)
                ok=self.k8s.deployment_ready(service)
            else:
                raise RuntimeError("Rollback is not enabled in this MVP.")
            incident.update({"result":"Recovery verified successfully." if ok else "Action completed but recovery verification timed out.",
                             "recovery_succeeded":bool(ok)})
            self._audit({"incident_id":incident["id"],"action":action,"service":service,"result":incident["result"]})
        except Exception as e:
            incident.update({"result":f"Execution failed: {e}","recovery_succeeded":False})
            self._audit({"incident_id":incident["id"],"action":action,"service":service,"result":"failed","error":str(e)})
        return incident
