# HandyConnect Makefile
# Comprehensive test-driven development configuration

.PHONY: help install test test-unit test-integration test-api test-analytics test-performance test-e2e test-slow test-fast test-all test-report clean setup-dev

# Default target
help:
	@echo "HandyConnect - Test-Driven Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup-dev     - Set up development environment"
	@echo "  install       - Install dependencies"
	@echo ""
	@echo "Test Commands:"
	@echo "  test          - Run all tests (default)"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-api      - Run API tests only"
	@echo "  test-analytics - Run analytics tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-e2e      - Run end-to-end tests only"
	@echo "  test-slow     - Run slow tests only"
	@echo "  test-fast     - Run fast tests only (exclude slow)"
	@echo "  test-all      - Run all tests with full coverage"
	@echo "  test-report   - Generate comprehensive test report"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean         - Clean up test artifacts"
	@echo "  run           - Run the application"
	@echo "  run-dev       - Run the application in development mode"
	@echo "  stop          - Stop the application"
	@echo "  logs          - View application logs"
	@echo ""

# Setup development environment
setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	venv\Scripts\activate && pip install --upgrade pip
	venv\Scripts\activate && pip install -r requirements.txt
	@echo "Development environment setup complete!"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed!"

# Test commands
test: test-fast

test-unit:
	@echo "Running unit tests..."
	python tests/test_runner.py --type unit

test-integration:
	@echo "Running integration tests..."
	python tests/test_runner.py --type integration

test-api:
	@echo "Running API tests..."
	python tests/test_runner.py --type api

test-analytics:
	@echo "Running analytics tests..."
	python tests/test_runner.py --type analytics

test-performance:
	@echo "Running performance tests..."
	python tests/test_runner.py --type performance

test-e2e:
	@echo "Running end-to-end tests..."
	python tests/test_runner.py --type e2e

test-slow:
	@echo "Running slow tests..."
	python tests/test_runner.py --type slow

test-fast:
	@echo "Running fast tests..."
	python tests/test_runner.py --type fast

test-all:
	@echo "Running all tests with full coverage..."
	python tests/test_runner.py --type all

test-report:
	@echo "Generating comprehensive test report..."
	python tests/test_runner.py --report

# Run specific test files
test-app:
	@echo "Running app tests..."
	python tests/test_runner.py --file test_app.py

test-email:
	@echo "Running email service tests..."
	python tests/test_runner.py --file test_email_service.py

test-llm:
	@echo "Running LLM service tests..."
	python tests/test_runner.py --file test_llm_service.py

test-task:
	@echo "Running task service tests..."
	python tests/test_runner.py --file test_task_service.py

test-threading:
	@echo "Running email threading tests..."
	python tests/test_runner.py --file test_email_threading.py

test-analytics-comprehensive:
	@echo "Running comprehensive analytics tests..."
	python tests/test_runner.py --file test_analytics_comprehensive.py

test-api-comprehensive:
	@echo "Running comprehensive API tests..."
	python tests/test_runner.py --file test_api_comprehensive.py

test-integration-comprehensive:
	@echo "Running comprehensive integration tests..."
	python tests/test_runner.py --file test_integration_comprehensive.py

# Application commands
run:
	@echo "Starting HandyConnect application..."
	python app.py

run-dev:
	@echo "Starting HandyConnect application in development mode..."
	@echo "Debug mode enabled, auto-reload enabled"
	python app.py

stop:
	@echo "Stopping HandyConnect application..."
	taskkill /F /IM python.exe 2>nul || echo "No Python processes found"

logs:
	@echo "Viewing application logs..."
	@if exist logs\app.log (type logs\app.log) else (echo "No log file found")

# Clean up
clean:
	@echo "Cleaning up test artifacts..."
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .coverage del .coverage
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist test_report.json del test_report.json
	@if exist test_report.html del test_report.html
	@if exist coverage.json del coverage.json
	@if exist data\analytics rmdir /s /q data\analytics
	@echo "Cleanup complete!"

# Development workflow
dev-setup: setup-dev
	@echo "Development setup complete! Run 'make run-dev' to start the application."

# CI/CD commands
ci-test:
	@echo "Running CI/CD test suite..."
	python tests/test_runner.py --type fast
	python tests/test_runner.py --type unit
	python tests/test_runner.py --type integration

ci-full-test:
	@echo "Running full CI/CD test suite..."
	python tests/test_runner.py --type all

# Coverage commands
coverage:
	@echo "Generating coverage report..."
	python -m pytest --cov=. --cov-report=html:htmlcov --cov-report=term-missing --cov-exclude=tests/* --cov-exclude=venv/* --cov-exclude=env/* tests/

coverage-report:
	@echo "Opening coverage report..."
	@if exist htmlcov\index.html (start htmlcov\index.html) else (echo "Coverage report not found. Run 'make coverage' first.")

# Linting and formatting
lint:
	@echo "Running linting..."
	@if exist .flake8 (flake8 .) else (echo "Flake8 not configured")
	@if exist .pylintrc (pylint *.py features/ tests/) else (echo "Pylint not configured")

format:
	@echo "Formatting code..."
	@if exist .black (black .) else (echo "Black not configured")
	@if exist .isort (isort .) else (echo "isort not configured")

# Database commands
db-init:
	@echo "Initializing database..."
	@if not exist data mkdir data
	@if not exist logs mkdir logs
	@echo "Database initialization complete!"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t handyconnect .

docker-run:
	@echo "Running Docker container..."
	docker run -p 5001:5001 handyconnect

docker-stop:
	@echo "Stopping Docker containers..."
	docker stop $$(docker ps -q --filter ancestor=handyconnect)

# Documentation
docs:
	@echo "Generating documentation..."
	@if exist docs (echo "Documentation already exists") else (echo "No documentation found")

# Health check
health:
	@echo "Checking application health..."
	@curl -s http://localhost:5001/api/health || echo "Application not running"

# Quick development cycle
dev-cycle: test-fast run-dev

# Full development cycle
full-cycle: test-all run-dev

# Production deployment
deploy:
	@echo "Deploying to production..."
	@echo "This would typically involve building, testing, and deploying to production"
	@echo "Implementation depends on your deployment strategy"

# Help for specific test types
help-tests:
	@echo "Test Type Descriptions:"
	@echo "======================"
	@echo "unit         - Fast, isolated tests for individual components"
	@echo "integration  - Tests for component interactions"
	@echo "api          - Tests for API endpoints"
	@echo "analytics    - Tests for analytics functionality"
	@echo "performance  - Tests for performance monitoring"
	@echo "e2e          - End-to-end user workflow tests"
	@echo "slow         - Tests that take longer to run"
	@echo "fast         - All tests except slow ones"
	@echo "all          - Complete test suite with full coverage"



