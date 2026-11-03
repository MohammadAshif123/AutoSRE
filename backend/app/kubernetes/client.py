from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os, time

class KubernetesManager:
    def __init__(self, namespace: str):
        self.namespace = namespace
        try:
            config.load_kube_config()
        except Exception:
            config.load_incluster_config()
        self.core = client.CoreV1Api()
        self.apps = client.AppsV1Api()

    def _allowed(self, namespace=None):
        return namespace in (None, self.namespace)

    def list_pods(self):
        return self.core.list_namespaced_pod(self.namespace).items

    def list_events(self):
        return self.core.list_namespaced_event(self.namespace).items

    def list_deployments(self):
        return self.apps.list_namespaced_deployment(self.namespace).items

    def get_pod(self, name):
        return self.core.read_namespaced_pod(name, self.namespace)

    def restart_pod(self, name):
        if not self._allowed(): raise PermissionError("Namespace is not allowed")
        self.core.delete_namespaced_pod(name, self.namespace)
        return f"Deleted pod {name}; Deployment will recreate it."

    def scale_deployment(self, name, replicas):
        if not self._allowed() or name not in {"frontend", "payment-service", "database"}:
            raise PermissionError("Deployment is not on the allowlist")
        body = {"spec": {"replicas": replicas}}
        self.apps.patch_namespaced_deployment_scale(name, self.namespace, body)
        return f"Scaled {name} to {replicas} replicas."

    def deployment_ready(self, name, timeout=45):
        deadline = time.time() + timeout
        while time.time() < deadline:
            d = self.apps.read_namespaced_deployment(name, self.namespace)
            if d.status.available_replicas == d.spec.replicas:
                return True
            time.sleep(2)
        return False
