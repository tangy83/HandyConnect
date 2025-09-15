# HandyConnect Makefile

.PHONY: help build run dev stop clean logs shell test setup

# Default target
help:
	@echo "HandyConnect - Available commands:"
	@echo "  build     - Build Docker image"
	@echo "  run       - Run in production mode"
	@echo "  dev       - Run in development mode"
	@echo "  stop      - Stop all services"
	@echo "  clean     - Clean up containers and images"
	@echo "  logs      - View application logs"
	@echo "  shell     - Open shell in running container"
	@echo "  test      - Run tests"
	@echo "  setup     - Initial setup"

# Build Docker image
build:
	docker-compose -f config/docker/docker-compose.yml build

# Run in production mode
run:
	docker-compose -f config/docker/docker-compose.yml up -d

# Run in development mode
dev:
	docker-compose -f config/docker/docker-compose.dev.yml up

# Stop all services
stop:
	docker-compose -f config/docker/docker-compose.yml down
	docker-compose -f config/docker/docker-compose.dev.yml down

# Clean up
clean:
	docker-compose -f config/docker/docker-compose.yml down -v --rmi all --remove-orphans
	docker system prune -f

# View logs
logs:
	docker-compose -f config/docker/docker-compose.yml logs -f handyconnect

# Open shell in container
shell:
	docker-compose -f config/docker/docker-compose.yml exec handyconnect /bin/bash

# Run tests
test:
	pytest tests/ -v --cov=. --cov-report=html

# Initial setup
setup:
	@echo "Setting up HandyConnect..."
	@if [ ! -f .env ]; then cp config/environment/env.example .env; echo "Created .env file - please configure it"; fi
	@mkdir -p data logs
	@python scripts/setup/verify_setup.py
	@echo "Setup complete! Configure your .env file and run 'make dev' to start"


