#!/bin/bash
set -e

echo "Deploying multo-agent system to Kubernetes..."

# Apply namespace
kubectl apply -f k8s/namespace.yaml

# Apply secrets (make sure to update with real values)
kubectl apply -f k8s/secrets.yaml

# Apply infrastructure components
echo "Deploying Redis..."
kubectl apply -f k8s/redis/

echo "Deploying RabbitMQ..."
kubectl apply -f k8s/rabbitmq/

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready..."
kubectl wait --for=condition=available deployment/redis -n multi-agent --timeout=300s
kubectl wait --for=condition=available deployment/rabbitmq -n multi-agent --timeout=300s

# Deploy agents
echo "Deploying agents..."
kubectl apply -f k8s/root-agent/
kubectl apply -f k8s/payment-agent/
kubectl apply -f k8s/search-agent/

# Apply ingress
kubectl apply -f k8s/ingress.yaml

# Apply network policies
kubectl apply -f k8s/network-policy.yaml

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/root-agent -n multi-agent --timeout=300s
kubectl wait --for=condition=available deployment/payment-agent -n multi-agent --timeout=300s
kubectl wait --for=condition=available deployment/search-agent -n multi-agent --timeout=300s

echo "Deployment completed successfully!"
echo "You can access the system at http://multi-agent.local"
echo ""
echo "To check status:"
echo "kubectl get pods -n multi-agent"
echo "kubectl get services -n multi-agent"
echo "kubectl get ingress -n multi-agent"