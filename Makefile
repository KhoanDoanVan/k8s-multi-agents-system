.PHONY: build deploy test clean local-up local-down

# Build all Docker images
build:
	@echo "Building Docker images..."
	@chmod +x scripts/build-images.sh
	@./scripts/build-images.sh

# Deploy to Kubernetes
deploy: build
	@echo "Deploying to Kubernetes..."
	@chmod +x scripts/deploy-k8s.sh
	@./scripts/deploy-k8s.sh

# Test the system
test:
	@echo "Testing system..."
	@chmod +x scripts/test-system.sh
	@./scripts/test-system.sh

# Test local Docker Compose setup
test-local:
	@echo "Testing local setup..."
	@chmod +x scripts/test-system.sh
	@./scripts/test-system.sh local

# Start local development environment
local-up:
	@echo "Starting local development environment..."
	@docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 30
	@$(MAKE) test-local

# Stop local development environment  
local-down:
	@echo "Stopping local development environment..."
	@docker-compose down -v

# Clean up everything
clean:
	@echo "Cleaning up..."
	@chmod +x scripts/cleanup.sh
	@./scripts/cleanup.sh

# Show system status
status:
	@echo "System Status:"
	@echo "=============="
	@kubectl get pods -n multi-agent 2>/dev/null || echo "Kubernetes not deployed"
	@echo ""
	@docker-compose ps 2>/dev/null || echo "Docker Compose not running"

# View logs
logs:
	@echo "Recent logs from all agents:"
	@kubectl logs -l app=root-agent -n multi-agent --tail=50 2>/dev/null || echo "No K8s logs"
	@docker-compose logs --tail=50 2>/dev/null || echo "No Docker logs"

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make deploy      - Deploy to Kubernetes"  
	@echo "  make test        - Test Kubernetes deployment"
	@echo "  make local-up    - Start local development"
	@echo "  make local-down  - Stop local development"
	@echo "  make test-local  - Test local deployment"
	@echo "  make clean       - Clean up everything"
	@echo "  make status      - Show system status"
	@echo "  make logs        - Show recent logs"
	@echo "  make help        - Show this help"