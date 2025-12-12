.PHONY: help lint test format run migrate makemigrations install install-dev clean db-up db-down db-logs

MANAGE = python core/sum_core/test_project/manage.py

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	pip install -e .

install-dev:
	pip install -U pip
	pip install -e ./core[dev]
	pre-commit install


lint: ## Run linting (ruff + mypy)
	ruff check .
	mypy . || true

test: ## Run tests with pytest
	python -m pytest

format: ## Format code with Black and isort
	black .
	isort .

run: ## Initial for local dev (may be wired to Docker later)
	$(MANAGE) migrate --noinput
	$(MANAGE) runserver

migrate: ## Apply database migrations for the test project
	$(MANAGE) migrate --noinput

makemigrations: ## Create new migrations for the test project
	$(MANAGE) makemigrations

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	rm -f .coverage .coverage.*

db-up: ## Start Postgres via Docker Compose
	docker-compose up -d db

db-down: ## Stop Postgres via Docker Compose
	docker-compose down

db-logs: ## Tail Postgres logs
	docker-compose logs -f db
