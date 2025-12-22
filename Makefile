.PHONY: help lint test test-cli test-themes test-templates test-fast format run migrate makemigrations install install-dev clean db-up db-down db-logs sync-cli-boilerplate check-cli-boilerplate release-check release-set-core-ref

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


lint: ## Run all linting and typechecking (strict)
	ruff check . --config pyproject.toml
	mypy core cli tests
	black --check core cli tests
	isort --check-only core cli tests

lint-strict: lint

format: ## Auto-format code
	black .
	isort .


test: ## Run tests with pytest
	python -m pytest

test-cli: ## Run CLI test slice only
	python -m pytest cli/tests -q

test-themes: ## Run themes test slice only
	python -m pytest tests/themes -q

test-templates: ## Run template loading order tests (fast gate)
	python -m pytest tests/templates/test_template_loading_order.py -q

test-fast: ## Run high-signal test slices (CLI + themes)
	python -m pytest cli/tests tests/themes -q

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

db-info: ## Show database configuration (project name, volume, connection details)
	@echo "=== Docker Compose Configuration ==="
	@if [ -f .env ]; then \
		PROJECT_NAME=$$(grep COMPOSE_PROJECT_NAME .env | cut -d'=' -f2); \
		echo "Project Name:    $$PROJECT_NAME"; \
		echo "Active Volume:   $${PROJECT_NAME}_sum_db_data"; \
	else \
		echo "Project Name:    <.env not found>"; \
		echo "Active Volume:   <unknown>"; \
	fi
	@echo ""
	@echo "=== All sum_db_data Volumes ==="
	@if [ -f .env ]; then \
		ACTIVE_VOL=$$(grep COMPOSE_PROJECT_NAME .env | cut -d'=' -f2)_sum_db_data; \
		docker volume ls --filter name=sum_db_data --format '{{.Name}}' | while read vol; do \
			created=$$(docker volume inspect $$vol --format '{{.CreatedAt}}' 2>/dev/null | cut -d'T' -f1); \
			if [ "$$vol" = "$$ACTIVE_VOL" ]; then \
				echo "  $$vol (created: $$created) ← ACTIVE"; \
			else \
				echo "  $$vol (created: $$created)"; \
			fi; \
		done || echo "  No volumes found"; \
	else \
		docker volume ls --filter name=sum_db_data --format '{{.Name}}' | while read vol; do \
			created=$$(docker volume inspect $$vol --format '{{.CreatedAt}}' 2>/dev/null | cut -d'T' -f1); \
			echo "  $$vol (created: $$created)"; \
		done || echo "  No volumes found"; \
	fi
	@echo ""
	@echo "=== Database Connection Details ==="
	@echo "DB Host:         $${DJANGO_DB_HOST:-localhost}"
	@echo "DB Port:         $${DJANGO_DB_PORT:-5432}"
	@echo "DB Name:         $${DJANGO_DB_NAME:-sum_db}"
	@echo "DB User:         $${DJANGO_DB_USER:-sum_user}"
	@echo ""
	@echo "=== Container Status ==="
	@docker-compose ps db 2>/dev/null || echo "Container not running (use 'make db-up')"

db-migrate-volume: ## Migrate data from old volume (e.g., tradesite_sum_db_data) to current volume
	@echo "This will copy data from tradesite_sum_db_data to the current active volume."
	@echo "WARNING: This will OVERWRITE any data in the current volume!"
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Stopping current database..."
	@docker-compose down
	@echo "Creating temporary container to copy data..."
	@docker run --rm \
		-v tradesite_sum_db_data:/source:ro \
		-v sumplatform_sum_db_data:/target \
		alpine sh -c "cd /source && cp -av . /target"
	@echo "Data migration complete. Starting database..."
	@docker-compose up -d db
	@echo "Done! Run 'make db-info' to verify."

sync-cli-boilerplate: ## Sync canonical boilerplate to CLI package
	python cli/scripts/sync_boilerplate.py

check-cli-boilerplate: ## Verify CLI boilerplate matches canonical (CI guard)
	python cli/scripts/sync_boilerplate.py --check

# --- Release Workflow Targets ---

release-check: lint test check-cli-boilerplate ## Run all pre-release checks (lint, test, drift)
	@echo ""
	@echo "[OK] All release checks passed."
	@echo "You can now run 'make release-set-core-ref REF=vX.Y.Z' to update boilerplate pinning."

release-set-core-ref: ## Update boilerplate to pin to a specific tag (usage: make release-set-core-ref REF=v0.1.0)
ifndef REF
	$(error REF is required. Usage: make release-set-core-ref REF=v0.1.0)
endif
	python scripts/set_boilerplate_core_ref.py --ref $(REF)
