# Multi-Agent Microservices Kubernetes System

Một hệ thống microservices multi-agent được xây dựng bằng Python và triển khai trên Kubernetes, sử dụng kiến trúc A2A (Agent-to-Agent) communication.

## 🏗️ Kiến Trúc Hệ Thống

### Components Chính

1. **Root Agent**: Agent chính có tích hợp LLM để phân tích và định tuyến requests
2. **Worker Agents**: Các microservices chuyên biệt (Payment, Search, v.v.)
3. **Message Broker**: RabbitMQ cho giao tiếp bất đồng bộ
4. **Load Balancer**: Nginx Ingress Controller
5. **Storage**: Redis cho caching, Persistent Volumes cho data

### Giao Tiếp A2A

Hệ thống hỗ trợ cả hai mô hình giao tiếp:
- **Synchronous (HTTP/JSON-RPC)**: Cho các requests urgent cần phản hồi ngay
- **Asynchronous (Message Queue)**: Cho các tasks phức tạp, tăng resilience

## 🚀 Quick Start

### Prerequisites

- Docker và Docker Compose
- Kubernetes cluster (minikube, kind, hoặc cloud provider)
- kubectl configured
- Make (optional, để sử dụng Makefile)

### 1. Local Development với Docker Compose

```bash
# Clone repository
git clone <your-repo-url>
cd multi-agent-k8s

# Start local development environment
make local-up

# Hoặc manually:
docker-compose up -d

# Test system
make test-local
```

### 2. Deploy lên Kubernetes

```bash
# Build và deploy
make deploy

# Hoặc manually:
./scripts/build-images.sh
./scripts/deploy-k8s.sh

# Test deployment  
make test
```

## 📝 API Usage

### Root Agent Endpoint

```bash
POST http://multi-agent.local/process
```

### Example Requests

#### Payment Request (Synchronous)
```json
{
  "message": "I want to pay $100 for order #12345",
  "user_id": "user-123",
  "context": {
    "order_id": "12345",
    "currency": "USD"
  }
}
```

#### Search Request (Asynchronous)
```json
{
  "message": "search for wireless headphones under $50",
  "user_id": "user-123", 
  "context": {
    "category": "electronics",
    "price_range": {"max": 50}
  }
}
```

### Response Format

```json
{
  "status": "success",
  "data": {
    "transaction_id": "txn_123456",
    "amount": 100.0,
    "currency": "USD", 
    "status": "completed"
  },
  "request_id": "req-uuid-here"
}
```

## 🔧 Configuration

### Environment Variables

#### Root Agent
- `OPENAI_API_KEY`: OpenAI API key cho LLM (optional)
- `RABBITMQ_URL`: RabbitMQ connection string
- `REDIS_URL`: Redis connection string

#### Payment Agent
- `PAYMENT_GATEWAY_URL`: Payment provider API URL
- `PAYMENT_API_KEY`: Payment provider API key

#### Search Agent
- `ELASTICSEARCH_URL`: Elasticsearch URL (nếu sử dụng)
- `SEARCH_INDEX`: Index name cho search

### Kubernetes Secrets

Update `k8s/secrets.yaml` với actual API keys:

```bash
# Encode your API keys
echo -n "your-openai-key" | base64
echo -n "your-payment-key" | base64

# Update secrets.yaml với encoded values
```

## 🛠️ Development

### Cấu trúc Project

```
multi-agent-k8s/
├── agents/                 # Agent implementations
│   ├── root_agent/        # LLM-powered request router
│   ├── payment_agent/     # Payment processing
│   ├── search_agent/      # Search functionality
│   └── shared/            # Shared libraries
├── k8s/                   # Kubernetes manifests
├── scripts/               # Deployment scripts
└── docker-compose.yml     # Local development
```

### Thêm Agent Mới

1. Tạo folder cho agent mới trong `agents/`
2. Implement FastAPI app với `/process` và `/health` endpoints
3. Tạo Dockerfile và requirements.txt
4. Tạo Kubernetes manifests trong `k8s/`
5. Update `agent_router.py` để include agent mới

### Local Testing

```bash
# Start services
make local-up

# Test individual agents
curl http://localhost:8001/health  # Payment agent
curl http://localhost:8002/health  # Search agent

# View logs
docker-compose logs -f root-agent
```

## 🚦 Monitoring và Health Checks

### Health Endpoints

- Root Agent: `GET /health`
- Payment Agent: `GET /health` 
- Search Agent: `GET /health`

### Kubernetes Status

```bash
# Check pod status
kubectl get pods -n multi-agent

# View logs
kubectl logs -f deployment/root-agent -n multi-agent

# Check HPA status
kubectl get hpa -n multi-agent
```

### Metrics

Các agents expose Prometheus metrics tại `/metrics` endpoint:

- Request count và latency
- Circuit breaker status
- Queue lengths
- Error rates

## 🔄 Scaling và Resilience

### Horizontal Pod Autoscaler (HPA)

```yaml
# Tự động scale dựa trên CPU và memory
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 70
```

### Circuit Breaker

Mỗi agent sử dụng circuit breaker pattern:

```python
# Tự động fail-fast khi downstream services có lỗi
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    recovery_threshold=3
)
```

### Message Queue Resilience

- Persistent queues với RabbitMQ
- Automatic retry với exponential backoff
- Dead letter queues cho failed messages

## 🔐 Security

### Network Policies

```bash
# Apply network segmentation
kubectl apply -f k8s/network-policy.yaml
```

### Secret Management

- Kubernetes Secrets cho sensitive data
- Non-root containers
- Resource limits và requests

## 🐛 Troubleshooting

### Common Issues

#### Pods không start được
```bash
kubectl describe pod <pod-name> -n multi-agent
kubectl logs <pod-name> -n multi-agent
```

#### RabbitMQ connection issues
```bash
# Check RabbitMQ status
kubectl exec -it deployment/rabbitmq -n multi-agent -- rabbitmq-diagnostics ping

# Access management UI (port-forward)
kubectl port-forward service/rabbitmq-service 15672:15672 -n multi-agent
# Truy cập http://localhost:15672 (guest/guest)
```

#### Ingress không work
```bash
# Check ingress controller
kubectl get ingressclass
kubectl describe ingress multi-agent-ingress -n multi-agent

# Add to /etc/hosts for local testing
echo "127.0.0.1 multi-agent.local" >> /etc/hosts
```

### Performance Tuning

#### Tăng throughput
```yaml
# Trong deployment.yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m  
    memory: 2Gi
```

#### Optimize RabbitMQ
```bash
# Increase connection pool
RABBITMQ_CONNECTION_POOL_SIZE=20
```

## 📊 Load Testing

### Sử dụng Apache Bench

```bash
# Test concurrent requests
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p test-payload.json \
   http://multi-agent.local/process
```

### Sử dụng k6

```javascript
// load-test.js
import http from 'k6/http';

export default function () {
  const payload = JSON.stringify({
    message: 'search for products',
    user_id: 'test-user'
  });
  
  http.post('http://multi-agent.local/process', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}

export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 0 },  // Ramp down
  ],
};
```

Run load test:
```bash
k6 run load-test.js
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Multi-Agent System

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/
    
    - name: Start test environment
      run: make local-up
    
    - name: Integration tests
      run: make test-local
    
    - name: Cleanup
      run: make local-down

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push images
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/multi-agent/root-agent:$IMAGE_TAG -f agents/root_agent/Dockerfile .
        docker build -t $ECR_REGISTRY/multi-agent/payment-agent:$IMAGE_TAG -f agents/payment_agent/Dockerfile .
        docker build -t $ECR_REGISTRY/multi-agent/search-agent:$IMAGE_TAG -f agents/search_agent/Dockerfile .
        
        docker push $ECR_REGISTRY/multi-agent/root-agent:$IMAGE_TAG
        docker push $ECR_REGISTRY/multi-agent/payment-agent:$IMAGE_TAG
        docker push $ECR_REGISTRY/multi-agent/search-agent:$IMAGE_TAG
    
    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --name production-cluster --region us-west-2
        
        # Update image tags in manifests
        sed -i "s|multi-agent/root-agent:latest|$ECR_REGISTRY/multi-agent/root-agent:$IMAGE_TAG|g" k8s/root-agent/deployment.yaml
        sed -i "s|multi-agent/payment-agent:latest|$ECR_REGISTRY/multi-agent/payment-agent:$IMAGE_TAG|g" k8s/payment-agent/deployment.yaml
        sed -i "s|multi-agent/search-agent:latest|$ECR_REGISTRY/multi-agent/search-agent:$IMAGE_TAG|g" k8s/search-agent/deployment.yaml
        
        # Deploy
        kubectl apply -f k8s/
        
        # Wait for rollout
        kubectl rollout status deployment/root-agent -n multi-agent
        kubectl rollout status deployment/payment-agent -n multi-agent
        kubectl rollout status deployment/search-agent -n multi-agent
```

## 🧪 Testing

### Unit Tests

```python
# tests/test_root_agent.py
import pytest
from httpx import AsyncClient
from agents.root_agent.app import app

@pytest.mark.asyncio
async def test_process_payment_request():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/process", json={
            "message": "pay $100",
            "user_id": "test-user"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
import asyncio
from agents.shared.a2a_client import A2AClient
from agents.shared.models import AgentRequest

@pytest.mark.asyncio
async def test_a2a_communication():
    client = A2AClient()
    request = AgentRequest(
        id="test-123",
        message="test payment",
        user_id="test-user"
    )
    
    # Test sync communication
    result = await client.send_sync_request("payment-agent-service", request)
    assert result["status"] == "success"
    
    # Test async communication
    result = await client.send_async_request("search-agent-service", request) 
    assert result["status"] == "queued"
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html

# Run specific test file
pytest tests/test_root_agent.py -v
```

## 📈 Monitoring và Observability

### Prometheus Metrics

```python
# agents/shared/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('agent_requests_total', 'Total requests', ['agent', 'method', 'status'])
REQUEST_DURATION = Histogram('agent_request_duration_seconds', 'Request duration', ['agent'])
ACTIVE_CONNECTIONS = Gauge('agent_active_connections', 'Active connections', ['agent'])

# Circuit breaker metrics
CIRCUIT_BREAKER_STATE = Gauge('circuit_breaker_state', 'Circuit breaker state', ['agent', 'target'])
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Multi-Agent System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_requests_total[5m])",
            "legendFormat": "{{agent}} - {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(agent_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Jaeger Tracing

```python
# agents/shared/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
```

## 🔒 Production Deployment

### AWS EKS Deployment

```bash
# Create EKS cluster
eksctl create cluster --name multi-agent-prod --region us-west-2 --nodes 3

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml

# Deploy application
make deploy

# Setup monitoring
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana/
```

### Google GKE Deployment

```bash
# Create GKE cluster
gcloud container clusters create multi-agent-prod \
    --zone us-central1-a \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10

# Get credentials
gcloud container clusters get-credentials multi-agent-prod --zone us-central1-a

# Deploy
make deploy
```

### Security Hardening

```yaml
# k8s/security/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 🚨 Disaster Recovery

### Backup Strategy

```bash
# Backup Kubernetes resources
kubectl get all -n multi-agent -o yaml > backup-$(date +%Y%m%d).yaml

# Backup RabbitMQ data
kubectl exec deployment/rabbitmq -n multi-agent -- rabbitmq-diagnostics export_definitions /tmp/definitions.json

# Backup Redis data
kubectl exec deployment/redis -n multi-agent -- redis-cli BGSAVE
```

### Recovery Procedures

```bash
# Restore from backup
kubectl apply -f backup-20231201.yaml

# Verify system health
make test

# Check data integrity
kubectl exec deployment/redis -n multi-agent -- redis-cli LASTSAVE
```

## 🤝 Contributing

### Development Setup

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-agent`
3. Make changes and test locally: `make local-up && make test-local`
4. Run tests: `pytest tests/`
5. Submit pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints
- Add docstrings for public methods
- Write tests for new features

### Commit Convention

```
feat: add new payment agent
fix: resolve circuit breaker timeout
docs: update README with deployment guide
test: add integration tests for A2A communication
```

## 📋 Roadmap

### Planned Features

- [ ] WebSocket support cho real-time communication
- [ ] GraphQL API gateway
- [ ] Machine learning agent cho predictive analytics
- [ ] Multi-tenancy support
- [ ] Advanced routing strategies
- [ ] Event sourcing implementation
- [ ] Distributed tracing with OpenTelemetry
- [ ] Chaos engineering tests

### Performance Goals

- Sub-100ms response time cho sync requests
- 10,000+ concurrent users support
- 99.9% uptime SLA
- Auto-scaling based on custom metrics

## 📞 Support

### Getting Help

- **Documentation**: Xem README và code comments
- **Issues**: Tạo GitHub issue với detailed description
- **Discussions**: Sử dụng GitHub Discussions cho questions

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check agent logs
kubectl logs -f deployment/root-agent -n multi-agent

# Inspect network traffic
kubectl exec -it deployment/root-agent -n multi-agent -- netstat -tulpn

# Database connection test
kubectl exec -it deployment/redis -n multi-agent -- redis-cli ping
```

## 🙏 Acknowledgments

- FastAPI team for excellent framework
- Kubernetes community for orchestration platform  
- RabbitMQ team for reliable messaging
- OpenAI for LLM capabilities

---