class GovernorAgent:
    # Transparent score: 50% diagnosis certainty + 25% evidence strength
    # + 15% historical success + 10% inverse action risk.
    RISK={"restart":("LOW",0.95),"scale":("MEDIUM",0.75),"rollback":("HIGH",0.45)}

    def evaluate(self, incident):
        action=incident.get("recommended_action")
        risk, risk_score=self.RISK.get(action,("HIGH",0.20))
        evidence=min(1.0, len(incident.get("evidence",[]))/3)
        history=0.5
        successful=[x for x in incident.get("similar_incidents",[])
                    if str(x.get("metadata",{}).get("recovery_succeeded","")).lower()=="true"]
        if successful: history=0.9
        certainty=incident.get("diagnosis_confidence",0)
        score=0.50*certainty+0.25*evidence+0.15*history+0.10*risk_score
        if score >= 0.80 and action in ("restart","scale"):
            decision="AUTO EXECUTE"
        elif score >= 0.60:
            decision="REQUIRE APPROVAL"
        else:
            decision="ESCALATE"
        incident.update({"governor_confidence":round(score,3),"decision":decision,"risk":risk})
        return incident
