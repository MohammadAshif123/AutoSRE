from datetime import datetime, timezone
import uuid

class ObserverAgent:
    def __init__(self, k8s):
        self.k8s=k8s

    def observe(self):
        incidents=[]
        for pod in self.k8s.list_pods():
            phase=pod.status.phase or ""
            statuses=pod.status.container_statuses or []
            restarts=sum((s.restart_count or 0) for s in statuses)
            waiting=[]
            for s in statuses:
                if s.state and s.state.waiting:
                    waiting.append(s.state.waiting.reason or "")
            reasons=set(waiting)
            if "CrashLoopBackOff" in reasons or restarts >= 3:
                evidence=[
                    {"source":"kubernetes","message":f"Pod {pod.metadata.name} phase={phase} restart_count={restarts}"},
                    {"source":"kubernetes","message":f"Container waiting reasons: {sorted(reasons) or ['none']}"}
                ]
                try:
                    logs=self.k8s.core.read_namespaced_pod_log(
                        pod.metadata.name, self.k8s.namespace, tail_lines=30
                    )
                    if logs:
                        evidence.append({"source":"logs","message":logs[-1000:]})
                except Exception as e:
                    evidence.append({"source":"logs","message":f"Log read unavailable: {e}"})
                incidents.append({
                    "id":"INC-"+uuid.uuid4().hex[:8].upper(),
                    "timestamp":datetime.now(timezone.utc).isoformat(),
                    "service": self._service(pod.metadata.labels or {}),
                    "namespace":self.k8s.namespace,
                    "symptom":"CrashLoopBackOff" if "CrashLoopBackOff" in reasons else "Repeated container restarts",
                    "evidence":evidence,
                    "status":"active"
                })
        return incidents

    def _service(self, labels):
        return labels.get("app") or labels.get("app.kubernetes.io/name") or "unknown"
