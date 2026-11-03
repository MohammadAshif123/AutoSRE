#!/usr/bin/env bash
set -e
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/frontend.yaml
