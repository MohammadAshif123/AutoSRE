# Troubleshooting

## Backend cannot connect to Kubernetes
Run `kubectl get nodes`. Make sure Minikube is running and the current kube-context is Minikube.

## Pods cannot pull images
Run `minikube status`, ensure Docker Desktop is running, then `kubectl -n autosre-demo describe pod <pod>`.

## Frontend says backend unavailable
Confirm `uvicorn app.main:app --reload --port 8000` is running.

## SAFE_MODE blocks recovery
This is intentional. Set `SAFE_MODE=false` only for the local demo and restart the backend.

## ChromaDB installation problem
The code has a JSON fallback for incident retrieval. Install the requirements again in Python 3.11.
