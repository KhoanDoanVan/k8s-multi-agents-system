#!/bin/bash
set -e

BASE_URL="http://multi-agent.local"
if [ "$1" = "local" ]; then
  BASE_URL="http://localhost"
fi

echo "Testing multi-agent system at $BASE_URL"

# Test root agent health
echo "Testing root agent health..."
curl -f "$BASE_URL/health" || { echo "Root agent health check failed"; exit 1; }

# Test payment request
echo "Testing payment request..."
curl -X POST "$BASE_URL/process" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to pay $100 for my order",
    "user_id": "test-user-123",
    "context": {"order_id": "order-456"}
  }' || { echo "Payment request test failed"; exit 1; }

# Test search request  
echo "Testing search request..."
curl -X POST "$BASE_URL/process" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "search for wireless headphones",
    "user_id": "test-user-123",
    "context": {"category": "electronics"}
  }' || { echo "Search request test failed"; exit 1; }

echo "All tests passed!"