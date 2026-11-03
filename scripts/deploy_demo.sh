kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/frontend.yaml
kubectl -n autosre-demo get pods
