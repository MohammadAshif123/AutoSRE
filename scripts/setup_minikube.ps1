$ErrorActionPreference="Stop"
Write-Host "Starting Minikube..."
minikube start --driver=docker
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/frontend.yaml
kubectl -n autosre-demo rollout status deployment/database --timeout=120s
kubectl -n autosre-demo rollout status deployment/payment-service --timeout=120s
kubectl -n autosre-demo rollout status deployment/frontend --timeout=120s
Write-Host "Demo cluster is ready."
