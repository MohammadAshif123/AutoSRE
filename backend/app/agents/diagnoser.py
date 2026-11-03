import re
import networkx as nx

class DiagnoserAgent:
    def __init__(self,k8s,memory):
        self.k8s=k8s
        self.memory=memory

    def dependency_graph(self):
        g=nx.DiGraph()
        for a,b in [("frontend","payment-service"),("payment-service","database")]:
            g.add_edge(a,b)
        return {n: list(g.successors(n)) for n in g.nodes}

    def diagnose(self, incident):
        text=" ".join(e["message"] for e in incident["evidence"]).lower()
        if "crashloopbackoff" in incident["symptom"].lower() or "crashloop" in text:
            cause="Payment application process is exiting repeatedly, causing Kubernetes to restart the container."
            conf=0.90
            action="restart"
        elif "memory" in text:
            cause="The payment workload shows a resource anomaly consistent with excessive memory use."
            conf=0.78
            action="restart"
        else:
            cause="Insufficient evidence for a safe root-cause conclusion."
            conf=0.35
            action=None
        incident.update({
            "root_cause":cause,
            "diagnosis_confidence":conf,
            "recommended_action":action,
            "dependencies":self.dependency_graph(),
        })
        incident["similar_incidents"]=self.memory.similar(incident)
        return incident
