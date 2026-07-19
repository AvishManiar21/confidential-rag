# ConfidentialRAG Makefile
# Convenient shortcuts for common development tasks

.PHONY: help setup start stop status health reset test deploy compile clean demo

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
help:
	@echo "$(BLUE)ConfidentialRAG - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make setup          - Install Midnight CLI and compile contract"
	@echo "  make setup-all      - Complete setup (all services)"
	@echo ""
	@echo "$(GREEN)Service Management:$(NC)"
	@echo "  make start          - Start all services (Docker + Midnight)"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make status         - Check Midnight development status"
	@echo "  make health         - Health check all services"
	@echo ""
	@echo "$(GREEN)Smart Contract:$(NC)"
	@echo "  make compile        - Compile Compact contract"
	@echo "  make deploy         - Deploy contract to local network"
	@echo "  make deploy-testnet - Deploy contract to testnet"
	@echo ""
	@echo "$(GREEN)Testing & Demo:$(NC)"
	@echo "  make test           - Run all tests"
	@echo "  make demo           - Upload demo data and run queries"
	@echo "  make demo-upload    - Upload medical abstracts"
	@echo "  make demo-query     - Run demo queries"
	@echo "  make demo-e2e       - Run end-to-end tests"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@echo "  make reset          - Reset PostgreSQL and ChromaDB"
	@echo "  make clean          - Clean all data and containers"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make logs           - Show Docker logs"
	@echo "  make logs-backend   - Show backend logs"
	@echo "  make shell-backend  - Shell into backend container"
	@echo ""

# Setup
setup:
	@echo "$(BLUE)[INFO]$(NC) Setting up Midnight development environment..."
	@./scripts/setup-midnight.sh

setup-all:
	@echo "$(BLUE)[INFO]$(NC) Running complete setup..."
	@./scripts/setup-all.sh

# Service management
start:
	@echo "$(BLUE)[INFO]$(NC) Starting all services..."
	@./scripts/start-all.sh

stop:
	@echo "$(BLUE)[INFO]$(NC) Stopping all services..."
	@./scripts/stop-all.sh

restart: stop start

status:
	@./scripts/check-midnight-status.sh

health:
	@./scripts/health-check.sh

# Smart contract
compile:
	@echo "$(BLUE)[INFO]$(NC) Compiling Compact contract..."
	@./scripts/compile-contract.sh

deploy:
	@echo "$(BLUE)[INFO]$(NC) Deploying contract to local network..."
	@./scripts/deploy-contract.sh local

deploy-testnet:
	@echo "$(BLUE)[INFO]$(NC) Deploying contract to testnet..."
	@./scripts/deploy-contract.sh testnet

# Testing
test:
	@echo "$(BLUE)[INFO]$(NC) Running test suite..."
	@./scripts/run-tests.sh

# Demo
demo: demo-upload demo-query

demo-upload:
	@echo "$(BLUE)[INFO]$(NC) Uploading demo data..."
	@python demo/upload-demo-data.py

demo-query:
	@echo "$(BLUE)[INFO]$(NC) Running demo queries..."
	@python demo/run-demo-queries.py

demo-e2e:
	@echo "$(BLUE)[INFO]$(NC) Running end-to-end tests..."
	@python demo/test-e2e.py

# Database
reset:
	@echo "$(YELLOW)[WARNING]$(NC) This will delete all data!"
	@./scripts/reset-db.sh

# Clean
clean:
	@echo "$(YELLOW)[WARNING]$(NC) Cleaning all containers and volumes..."
	@docker-compose down -v
	@rm -f .midnight-network.pid
	@rm -f contracts/deployment.log
	@rm -f contracts/deployment-info.json
	@echo "$(GREEN)[SUCCESS]$(NC) Cleanup complete!"

# Logs
logs:
	@docker-compose logs -f

logs-backend:
	@docker-compose logs -f backend

logs-frontend:
	@docker-compose logs -f frontend

logs-postgres:
	@docker-compose logs -f postgres

logs-chromadb:
	@docker-compose logs -f chromadb

# Development
shell-backend:
	@docker exec -it confidential-rag-backend /bin/bash

shell-postgres:
	@docker exec -it confidential-rag-postgres psql -U raguser -d confidentialrag

# Quick start (most common workflow)
quickstart: setup start demo
	@echo ""
	@echo "$(GREEN)[SUCCESS]$(NC) Quick start complete!"
	@echo ""
	@echo "Services running at:"
	@echo "  Frontend:  http://localhost:8501"
	@echo "  Backend:   http://localhost:8001"
	@echo "  API Docs:  http://localhost:8001/docs"
	@echo ""

# Install Python dependencies
install-python:
	@cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)[SUCCESS]$(NC) Python dependencies installed!"

# Initialize database
init-db:
	@cd backend && source venv/bin/activate && python setup_db.py
	@echo "$(GREEN)[SUCCESS]$(NC) Database initialized!"
