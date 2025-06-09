# Meeting AI Development Makefile

.PHONY: help setup start stop restart build test lint format clean logs

# Default target
help:
	@echo "Meeting AI Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup & Environment:"
	@echo "  setup          Setup development environment"
	@echo "  env            Copy environment files"
	@echo ""
	@echo "Development:"
	@echo "  start          Start all services"
	@echo "  stop           Stop all services"
	@echo "  restart        Restart all services"
	@echo "  logs           Show service logs"
	@echo ""
	@echo "Building:"
	@echo "  build          Build Docker images"
	@echo "  build-backend  Build backend Docker image"
	@echo "  build-frontend Build frontend Docker image"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate     Run database migrations"
	@echo "  db-reset       Reset database"
	@echo "  db-seed        Seed database with sample data"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-backend   Run backend tests"
	@echo "  test-frontend  Run frontend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           Run linting"
	@echo "  format         Format code"
	@echo "  type-check     Run type checking"
	@echo ""
	@echo "Infrastructure:"
	@echo "  infra-plan     Plan infrastructure changes"
	@echo "  infra-apply    Apply infrastructure changes"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          Clean up containers and volumes"
	@echo "  clean-all      Clean everything including images"

# Setup commands
setup: env
	@echo "Setting up development environment..."
	docker-compose pull
	$(MAKE) build
	$(MAKE) db-migrate
	@echo "Setup complete! Run 'make start' to begin development."

env:
	@echo "Creating environment files..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env"; fi
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env"; fi
	@if [ ! -f frontend/.env.local ]; then cp frontend/.env.example frontend/.env.local; echo "Created frontend/.env.local"; fi

# Development commands
start:
	@echo "Starting Meeting AI development environment..."
	docker-compose up -d
	@echo "Services starting. Use 'make logs' to view output."
	@echo ""
	@echo "Services will be available at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

stop:
	@echo "Stopping services..."
	docker-compose down

restart:
	@echo "Restarting services..."
	docker-compose down
	docker-compose up -d

logs:
	docker-compose logs -f

# Build commands
build:
	@echo "Building Docker images..."
	docker-compose build

build-backend:
	@echo "Building backend Docker image..."
	docker-compose build backend

build-frontend:
	@echo "Building frontend Docker image..."
	docker-compose build frontend

# Database commands
db-migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres redis
	sleep 10
	$(MAKE) db-migrate

db-seed:
	@echo "Seeding database..."
	docker-compose exec backend python scripts/seed_data.py

# Testing commands
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	docker-compose exec backend pytest -v

test-frontend:
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test

# Code quality commands
lint:
	@echo "Running linting..."
	docker-compose exec backend poetry run ruff check .
	docker-compose exec frontend npm run lint

format:
	@echo "Formatting code..."
	docker-compose exec backend poetry run black .
	docker-compose exec backend poetry run ruff --fix .
	docker-compose exec frontend npm run format

type-check:
	@echo "Running type checking..."
	docker-compose exec backend poetry run mypy .
	docker-compose exec frontend npm run type-check

# Infrastructure commands
infra-plan:
	@echo "Planning infrastructure changes..."
	cd infrastructure/environments/dev && terraform plan

infra-apply:
	@echo "Applying infrastructure changes..."
	cd infrastructure/environments/dev && terraform apply

# Maintenance commands
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

clean-all:
	@echo "Cleaning everything..."
	docker-compose down -v --rmi all
	docker system prune -af
	docker volume prune -f

# Development helpers
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

shell-db:
	docker-compose exec postgres psql -U meeting_ai -d meeting_ai_db

# Monitoring
stats:
	@echo "Container resource usage:"
	docker stats --no-stream

ps:
	@echo "Running containers:"
	docker-compose ps