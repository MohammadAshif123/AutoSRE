````markdown
# AutoSRE – Agentic Self-Healing System for Autonomous Kubernetes Operations

AutoSRE is a local, free, agentic self-healing system for Kubernetes that detects failures, diagnoses their cause, decides whether an automated action is safe, executes the recovery action, verifies recovery, and stores the incident for future retrieval.

The system implements:

**Detect → Diagnose → Decide → Act → Learn**

The MVP runs locally on **Minikube** and does not require OpenAI, Claude, Gemini, AWS, Azure, or GCP APIs.

---

## Overview

AutoSRE demonstrates how an agentic system can automate Kubernetes failure detection, diagnosis, governance, recovery, and incident learning.

The main workflow is:

```text
Failure
   ↓
Observer
   ↓
Diagnoser
   ↓
Incident Memory
   ↓
Governor
   ↓
Executor
   ↓
Kubernetes Recovery
   ↓
Recovery Verification
   ↓
Incident Memory
````

The MVP focuses on one complete end-to-end scenario:

```text
payment-service CrashLoopBackOff
        ↓
Observer detects failure
        ↓
Diagnoser identifies the cause
        ↓
Similar incidents retrieved
        ↓
Governor evaluates confidence and risk
        ↓
Executor restarts payment-service
        ↓
Kubernetes recovers
        ↓
Recovery is verified
        ↓
Incident is stored
```

---

# Features

* Local Kubernetes cluster using Minikube
* Kubernetes pod monitoring
* Pod restart-count monitoring
* Container waiting-reason detection
* Container log collection
* Deterministic rule-based diagnosis
* Transparent Governor confidence scoring
* Automatic Kubernetes recovery
* SAFE_MODE protection
* Kubernetes namespace/resource/action allowlists
* Recovery verification
* Persistent ChromaDB incident memory
* JSON fallback incident storage
* NetworkX dependency graph
* React + Vite dashboard
* FastAPI backend
* Payment-service crash simulation
* Incident history
* Audit logging
* API endpoints
* Unit and API tests
* No external paid APIs required

---

# What Actually Works

The current MVP has been tested end-to-end.

### Kubernetes

* Minikube
* Kubernetes API access
* Demo namespace
* Three-service demo application
* Pod monitoring
* Pod restart
* Deployment scaling

### AutoSRE Agents

* ObserverAgent
* DiagnoserAgent
* GovernorAgent
* ExecutorAgent
* IncidentMemory

### Dashboard

* Cluster status
* Kubernetes namespace
* Pod status
* Incident count
* Agent activity
* Dependency graph
* Failure simulation
* Observe + Diagnose
* Restart action
* Recovery status
* Incident information

### Reliability Workflow

```text
Payment Service Crash
        ↓
Observer detects incident
        ↓
Diagnoser identifies CrashLoopBackOff
        ↓
Incident Memory retrieves similar incidents
        ↓
Governor calculates confidence
        ↓
Governor selects AUTO EXECUTE
        ↓
Executor restarts payment-service
        ↓
Kubernetes recovers the pod
        ↓
Executor verifies recovery
        ↓
Incident stored in memory
```

---

# Architecture

```text
                    ┌─────────────────────┐
                    │   React Dashboard   │
                    │      Vite UI        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Orchestrator      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌───────────┐    ┌───────────┐
        │ Observer │ ──► │ Diagnoser  │ ─► │ Governor  │
        └──────────┘     └───────────┘    └─────┬─────┘
                                                  │
                                                  ▼
                                           ┌────────────┐
                                           │  Executor  │
                                           └─────┬──────┘
                                                 │
                                                 ▼
                                          Kubernetes API
                                                 │
                                                 ▼
                                        Recovery Verification
                                                 │
                                                 ▼
                                         Incident Memory
                                                 │
                                                 ▼
                                             ChromaDB
```

---

# Demo Application

The demo consists of three Kubernetes services:

```text
frontend
    │
    ▼
payment-service
    │
    ▼
database
```

All services run inside:

```text
autosre-demo
```

The main failure scenario is:

```text
payment-service
      ↓
container crash
      ↓
Kubernetes restart attempts
      ↓
CrashLoopBackOff
      ↓
AutoSRE detection
      ↓
automatic recovery
```

---

# Agents

## 1. ObserverAgent

The Observer monitors Kubernetes and collects evidence about the current state of the cluster.

It reads:

* Pod status
* Container status
* Restart counts
* Waiting reasons
* Container logs
* Service information

The Observer converts Kubernetes information into a structured incident.

Example:

```text
Service:
payment-service

Phase:
Running

Waiting Reason:
CrashLoopBackOff

Restart Count:
multiple restarts
```

---

## 2. DiagnoserAgent

The Diagnoser uses deterministic evidence-based rules.

No external LLM is required.

For example:

```text
CrashLoopBackOff
        +
Repeated container restarts
        ↓
Process-exit / application crash diagnosis
```

The Diagnoser also:

* collects supporting evidence
* identifies the affected service
* identifies dependencies
* retrieves similar historical incidents
* produces a diagnosis confidence value

---

## 3. GovernorAgent

The Governor determines whether the recommended action should be:

```text
AUTO EXECUTE
REQUIRE APPROVAL
ESCALATE
```

The confidence score is calculated using:

```text
Score =
0.50 × diagnosis certainty
+
0.25 × evidence strength
+
0.15 × historical success
+
0.10 × inverse action risk
```

Decision thresholds:

```text
Score >= 0.80
        ↓
AUTO EXECUTE

Score >= 0.60
        ↓
REQUIRE APPROVAL

Score < 0.60
        ↓
ESCALATE
```

This is an explicit scoring mechanism rather than an unexplained LLM confidence value.

---

## 4. ExecutorAgent

The Executor performs approved Kubernetes actions.

The MVP supports:

```text
restart
scale
```

The Executor enforces:

### Namespace allowlist

```text
autosre-demo
```

### Resource allowlist

```text
frontend
payment-service
database
```

### Action allowlist

Only known action names are accepted.

### SAFE_MODE

When enabled:

```env
SAFE_MODE=true
```

Kubernetes mutations are blocked.

When disabled:

```env
SAFE_MODE=false
```

allowlisted recovery actions can be executed.

### Audit Logging

Every attempted action is audited.

Rollback is intentionally blocked in this MVP until safe revision validation is implemented.

---

# Incident Memory

AutoSRE uses ChromaDB as persistent incident memory.

Stored incident information includes:

* Incident ID
* Timestamp
* Service
* Symptoms
* Evidence
* Root cause
* Selected action
* Confidence
* Recovery result

The system can retrieve similar historical incidents.

```text
Current Incident
       ↓
Embedding
       ↓
ChromaDB
       ↓
Similar Historical Incidents
       ↓
Diagnosis / Governance Context
```

This is referred to as **vector-based incident memory/retrieval**.

It is not reinforcement learning.

A small JSON fallback is also available for constrained installations.

---

# Dependency Graph

AutoSRE uses NetworkX to represent service dependencies.

The demo dependency graph is:

```text
frontend → payment-service → database
```

---

# Technology Stack

## Backend

* Python
* FastAPI
* Kubernetes Python Client
* ChromaDB
* NetworkX
* Pydantic
* Uvicorn
* pytest

## Frontend

* React
* Vite
* JavaScript

## Infrastructure

* Docker Desktop
* Minikube
* Kubernetes
* kubectl

## Incident Memory

* ChromaDB
* JSON fallback

## Optional AI

* Ollama

The core MVP does not require an external LLM.

---

# Project Structure

```text
AutoSRE/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── observer.py
│   │   │   ├── diagnoser.py
│   │   │   ├── governor.py
│   │   │   ├── executor.py
│   │   │   └── orchestrator.py
│   │   │
│   │   ├── memory/
│   │   │   └── incident_memory.py
│   │   │
│   │   ├── config.py
│   │   ├── main.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── k8s/
│   ├── namespace.yaml
│   ├── database.yaml
│   ├── payment-service.yaml
│   ├── frontend.yaml
│   └── ...
│
├── scripts/
│   ├── setup_minikube.ps1
│   ├── deploy_demo.ps1
│   └── simulate_failure.py
│
├── tests/
│   ├── test_diagnosis.py
│   ├── test_executor.py
│   ├── test_governor.py
│   └── test_health.py
│
├── data/
│   └── chroma/
│
├── docs/
│
├── .env.example
├── pytest.ini
├── .gitignore
└── README.md
```

---

# Requirements

The project is designed for local Windows development.

Install:

1. Docker Desktop
2. Minikube
3. kubectl
4. Python 3.11+
5. Node.js 20+

Recommended:

* Windows 10/11
* Windows PowerShell
* Docker Desktop with WSL2 backend

---

# Verify Installation

Open PowerShell:

```powershell
docker --version
minikube version
kubectl version --client
python --version
node --version
npm --version
```

---

# Quick Start

## 1. Start Kubernetes

From the project root:

```powershell
minikube start --driver=docker
```

Verify:

```powershell
kubectl get nodes
```

The Minikube node should show:

```text
Ready
```

---

## 2. Deploy the Demo

From the project root:

```powershell
.\scripts\deploy_demo.ps1
```

If PowerShell blocks the script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\scripts\deploy_demo.ps1
```

Check the pods:

```powershell
kubectl -n autosre-demo get pods
```

The three demo services should eventually show:

```text
Running
```

---

# Backend Setup

Open PowerShell terminal 1.

From the project root:

```powershell
cd backend
```

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create the local environment file:

```powershell
copy ..\.env.example .env
```

Return to the project root:

```powershell
cd ..
```

Start the backend:

```powershell
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/health
```

---

# Frontend Setup

Open PowerShell terminal 2.

From the project root:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start Vite:

```powershell
npm run dev
```

Open the URL shown by Vite.

Usually:

```text
http://localhost:5173
```

---

# SAFE_MODE

SAFE_MODE is an important safety feature.

## Safe Mode

The default configuration is:

```env
SAFE_MODE=true
```

In this mode:

* incidents can be detected
* incidents can be diagnosed
* Governor decisions can be calculated
* recommended actions can be displayed

But Kubernetes mutations are blocked.

---

## Autonomous Recovery Mode

For the local self-healing demonstration only:

```env
SAFE_MODE=false
```

Restart the backend after changing `.env`.

Only the allowlisted demo namespace and resources can be modified.

Do not point this MVP at a production Kubernetes cluster.

---

# End-to-End Demo

## 1. Start the system

Make sure:

* Docker Desktop is running
* Minikube is running
* Kubernetes demo is deployed
* Backend is running
* Frontend is running

---

## 2. Open the Dashboard

Open:

```text
http://localhost:5173
```

The dashboard should initially show a healthy cluster.

Example:

```text
Cluster: OK
Namespace: autosre-demo
Pods: 3/3
```

---

## 3. Trigger the Failure

Click:

```text
Trigger Payment Crash
```

This simulates a failure in:

```text
payment-service
```

---

## 4. Watch Kubernetes

Open another PowerShell terminal:

```powershell
kubectl -n autosre-demo get pods -w
```

The payment service should experience restart attempts.

Eventually Kubernetes may report:

```text
CrashLoopBackOff
```

---

## 5. Observe and Diagnose

Return to the dashboard.

Click:

```text
Observe + Diagnose
```

The system performs:

```text
Observer
   ↓
Diagnoser
   ↓
Incident Memory
   ↓
Governor
```

The dashboard displays information such as:

```text
Affected Service:
payment-service

Diagnosis:
CrashLoopBackOff / process exit

Evidence:
Repeated container restarts

Similar Incidents:
Historical matches from ChromaDB

Governor:
AUTO EXECUTE

Recommended Action:
restart
```

---

## 6. Execute Recovery

If:

```env
SAFE_MODE=false
```

the Executor can perform the allowlisted restart.

The workflow becomes:

```text
Governor
   ↓
AUTO EXECUTE
   ↓
Executor
   ↓
Restart payment-service
   ↓
Kubernetes
   ↓
Recovery verification
```

---

## 7. Verify Recovery

Run:

```powershell
kubectl -n autosre-demo get pods
```

Expected final state:

```text
frontend          Running
payment-service   Running
database          Running
```

The dashboard should show successful recovery verification.

---

## 8. Incident Memory

After the incident is processed, AutoSRE stores the incident.

Future incidents can retrieve similar historical incidents from ChromaDB.

---

# CLI Failure Simulation

The failure can also be triggered without using the dashboard.

From the project root:

```powershell
python scripts/simulate_failure.py --type crash
```

Then:

```powershell
kubectl -n autosre-demo get pods
```

After the failure becomes visible, use the dashboard's:

```text
Observe + Diagnose
```

button.

---

# API

| Method | Endpoint             | Purpose                      |
| ------ | -------------------- | ---------------------------- |
| GET    | `/health`            | Backend health               |
| GET    | `/cluster/status`    | Kubernetes cluster status    |
| GET    | `/services`          | Demo services                |
| GET    | `/incidents`         | Incident list                |
| GET    | `/incidents/{id}`    | Incident details             |
| POST   | `/incidents/analyze` | Analyze current incidents    |
| POST   | `/actions/restart`   | Restart allowlisted service  |
| POST   | `/actions/scale`     | Scale allowlisted deployment |
| POST   | `/actions/rollback`  | Rollback endpoint            |
| POST   | `/simulate/failure`  | Simulate failure             |
| POST   | `/query`             | Query incident information   |

---

# Testing

The project includes automated backend tests.

From the **project root**:

```powershell
.\backend\.venv\Scripts\Activate.ps1
pytest -q
```

Expected result:

```text
6 passed
```

The repository includes:

```text
pytest.ini
```

which configures the backend package path for testing.

---

# Security Model

AutoSRE restricts Kubernetes operations to the demo environment.

### Namespace restriction

```text
autosre-demo
```

### Resource restriction

```text
frontend
payment-service
database
```

### Action restriction

Only allowlisted actions are accepted.

### SAFE_MODE

Kubernetes mutations can be disabled using:

```env
SAFE_MODE=true
```

### Audit Logging

Attempted actions are recorded.

---

# Security Notice

This project is a local MVP.

Do not connect it to a production Kubernetes cluster.

A production implementation should additionally use:

* Kubernetes RBAC
* Dedicated ServiceAccounts
* Authentication
* Authorization
* Human approval workflows
* Validated rollback
* Production monitoring
* Stronger audit controls

---

# Optional Observability

The core MVP does not require:

* Prometheus
* Grafana
* Loki
* OpenTelemetry

The Observer can operate using Kubernetes API information and container logs.

These tools can be integrated later for richer observability.

---

# Optional Local LLM

AutoSRE can optionally use Ollama as a local LLM layer.

The core MVP does not require an external LLM.

Configure:

```env
OLLAMA_ENABLED=true
OLLAMA_MODEL=<local-model>
OLLAMA_URL=http://localhost:11434
```

The deterministic diagnosis path remains available when Ollama is disabled.

No external API key is required.

---

# No Paid Cloud Dependencies

The MVP does not require:

* OpenAI API
* Claude API
* Gemini API
* AWS
* Azure
* Google Cloud
* Paid Kubernetes services

The intended environment is completely local.

---

# ChromaDB Note

ChromaDB uses a local embedding model for vector retrieval.

On a fresh installation, the embedding model may need to be downloaded.

The download may take some time depending on:

* Internet speed
* System performance
* ChromaDB version
* Local cache state

Once downloaded, the model is cached locally.

The project also contains a JSON fallback for constrained installations.

---

# Configuration

Example configuration:

```env
K8S_NAMESPACE=autosre-demo
SAFE_MODE=true
OLLAMA_ENABLED=false
OLLAMA_MODEL=
OLLAMA_URL=http://localhost:11434
PROMETHEUS_URL=
LOKI_URL=
CHROMA_PATH=./data/chroma
```

For local autonomous recovery testing:

```env
SAFE_MODE=false
```

Keep your local:

```text
.env
```

private and do not commit it to Git.

Commit:

```text
.env.example
```

instead.

---

# Troubleshooting

## Minikube is not running

```powershell
minikube start --driver=docker
```

Check:

```powershell
minikube status
```

---

## Kubernetes pods are not running

```powershell
kubectl -n autosre-demo get pods
```

For details:

```powershell
kubectl -n autosre-demo describe pod <pod-name>
```

For logs:

```powershell
kubectl -n autosre-demo logs <pod-name>
```

---

## PowerShell blocks a script

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## Backend cannot find FastAPI

Activate the virtual environment:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the backend from the project root:

```powershell
cd ..
uvicorn app.main:app --app-dir backend --reload --port 8000
```

---

## Frontend dependencies are missing

```powershell
cd frontend
npm install
npm run dev
```

---

## SAFE_MODE blocks recovery

Check:

```env
SAFE_MODE=true
```

For the local autonomous recovery demonstration:

```env
SAFE_MODE=false
```

Restart the backend after changing the value.

---

# Known Limitations

* The primary diagnosis engine is deterministic rather than a trained ML model.
* Prometheus and Loki are not deeply integrated into the base MVP.
* Rollback is intentionally blocked until safe revision validation is implemented.
* Production authentication and multi-user authorization are outside the MVP.
* Production Kubernetes RBAC is not included.
* Demo services use simple containers rather than production application images.
* ChromaDB retrieval quality depends on local embedding configuration and available historical incidents.
* The MVP focuses primarily on the payment-service CrashLoopBackOff scenario.

---

# Future Improvements

* Real Prometheus metric ingestion
* Alert correlation
* Loki log querying
* OpenTelemetry traces
* Namespace-scoped Kubernetes RBAC
* Dedicated Kubernetes ServiceAccount
* Validated rollout-history rollback
* Human approval workflow
* Richer dependency discovery
* Kubernetes Service/Ingress graph discovery
* Local Ollama explanation layer
* Incident analytics
* Automatic postmortem generation
* Additional failure simulations
* Resource anomaly detection
* Latency anomaly detection
* More sophisticated incident similarity retrieval

---

# Design Philosophy

AutoSRE prioritizes:

```text
Safety
   ↓
Explainability
   ↓
Deterministic behavior
   ↓
Controlled automation
   ↓
Recovery verification
   ↓
Learning from incidents
```

Instead of relying entirely on an LLM, the MVP uses explicit rules and confidence scoring for critical operational decisions.

This makes the system:

* Reproducible
* Locally runnable
* Explainable
* Testable
* Inexpensive
* Safer to demonstrate

---

# End-to-End Workflow

```text
┌──────────────────────┐
│ Kubernetes Failure   │
│ payment-service      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ ObserverAgent        │
│ Detects failure      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ DiagnoserAgent       │
│ Determines cause     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Incident Memory      │
│ Similar incidents    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ GovernorAgent        │
│ Confidence + Risk    │
└──────────┬───────────┘
           ↓
     ┌─────┴─────┐
     │           │
     ▼           ▼
 APPROVAL     AUTO EXECUTE
                   │
                   ▼
          ┌────────────────┐
          │ ExecutorAgent  │
          │ Restart pod    │
          └───────┬────────┘
                  ↓
          ┌────────────────┐
          │ Kubernetes     │
          │ Recovery       │
          └───────┬────────┘
                  ↓
          ┌────────────────┐
          │ Recovery       │
          │ Verification   │
          └───────┬────────┘
                  ↓
          ┌────────────────┐
          │ Incident       │
          │ Memory         │
          └────────────────┘
```

---

# Quick Command Reference

### Start Kubernetes

```powershell
minikube start --driver=docker
```

### Deploy demo

```powershell
.\scripts\deploy_demo.ps1
```

### Check pods

```powershell
kubectl -n autosre-demo get pods
```

### Watch pods

```powershell
kubectl -n autosre-demo get pods -w
```

### Start backend

```powershell
.\backend\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Start frontend

```powershell
cd frontend
npm run dev
```

### Trigger crash

```powershell
python scripts/simulate_failure.py --type crash
```

### Run tests

```powershell
.\backend\.venv\Scripts\Activate.ps1
pytest -q
```

---

# Project Status

## MVP Complete

The core AutoSRE MVP successfully demonstrates:

```text
Detect
  ↓
Diagnose
  ↓
Decide
  ↓
Act
  ↓
Recover
  ↓
Learn
```

The primary end-to-end Kubernetes self-healing workflow has been implemented and tested locally.

---

# License

This project is intended as a personal/local engineering project and demonstration of autonomous Kubernetes reliability concepts.

```
```
