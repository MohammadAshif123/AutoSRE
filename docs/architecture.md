# Architecture

AutoSRE is deliberately built as a clean Python orchestrator rather than introducing LangGraph overhead for the MVP.

## Flow

1. Observer queries Kubernetes.
2. Incident is normalized.
3. Diagnoser evaluates evidence and retrieves similar incidents.
4. Governor computes an explicit confidence score.
5. Executor performs only allowlisted actions when allowed.
6. Recovery is verified through Deployment availability.
7. Incident is stored in ChromaDB.

## Why no LangGraph?

The hackathon's core value is the actual closed-loop Kubernetes operation. A small class-based orchestrator is easier to run, debug and explain than adding a graph framework when the workflow is linear and deterministic.
