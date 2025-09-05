#!/bin/bash
set -e

echo "Building multi-agent microservices images..."

# Build root agent
echo "Building root-agent..."
docker build -t multi-agent/root-agent:latest -f agents/root_agent/Dockerfile .

# Build payment agent
echo "Building payment-agent..."
docker build -t multi-agent/payment-agent:latest -f agents/payment_agent/Dockerfile .

# Build search agent
echo "Building search-agent..."
docker build -t multi-agent/search-agent:latest -f agents/search_agent/Dockerfile .

echo "All images built successfully!"