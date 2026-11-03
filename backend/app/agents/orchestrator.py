class Orchestrator:
    def __init__(self,observer,diagnoser,governor,executor,memory):
        self.observer=observer; self.diagnoser=diagnoser; self.governor=governor
        self.executor=executor; self.memory=memory

    def process(self, incident, execute=False):
        incident=self.diagnoser.diagnose(incident)
        incident=self.governor.evaluate(incident)
        incident["action"]=incident.get("recommended_action")
        if execute and incident.get("decision")=="AUTO EXECUTE":
            incident=self.executor.execute(incident)
        self.memory.add(incident)
        return incident
