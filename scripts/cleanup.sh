#!/bin/bash
set -e

echo "Cleaning up multi-agent system..."

# Delete all resources in the namespace
kubectl delete namespace multi-agent --ignore-not-found=true

# Remove local Docker images
docker rmi multi-agent/root-agent:latest || true
docker rmi multi-agent/payment-agent:latest || true
docker rmi multi-agent/search-agent:latest || true

# Clean up Docker compose
docker-compose down -v || true

echo "Cleanup completed!"