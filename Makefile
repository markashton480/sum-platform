.PHONY: help lint typecheck test test-integration test-full test-e2e test-cli test-themes test-templates test-fast verify-source-intact format run migrate makemigrations install install-dev clean db-up db-down db-logs sync-cli-boilerplate check-cli-boilerplate release-check release-set-core-ref preflight

MANAGE = python core/sum_core/test_project/manage.py
PYREFLY_REPLACE_IMPORTS = \
	--replace-imports-with-any django \
	--replace-imports-with-any django.apps \
	--replace-imports-with-any django.conf \
	--replace-imports-with-any django.contrib \
	--replace-imports-with-any django.contrib.admin.utils \
	--replace-imports-with-any django.contrib.auth.models \
	--replace-imports-with-any django.contrib.contenttypes.models \
	--replace-imports-with-any django.core \
	--replace-imports-with-any django.core.cache \
	--replace-imports-with-any django.core.exceptions \
	--replace-imports-with-any django.core.files.storage \
	--replace-imports-with-any django.core.files.uploadedfile \
	--replace-imports-with-any django.core.mail \
	--replace-imports-with-any django.core.validators \
	--replace-imports-with-any django.db \
	--replace-imports-with-any django.db.models \
	--replace-imports-with-any django.db.models.functions \
	--replace-imports-with-any django.db.models.signals \
	--replace-imports-with-any django.dispatch \
	--replace-imports-with-any django.http \
	--replace-imports-with-any django.shortcuts \
	--replace-imports-with-any django.template \
	--replace-imports-with-any django.template.loader \
	--replace-imports-with-any django.urls \
	--replace-imports-with-any django.utils \
	--replace-imports-with-any django.utils.decorators \
	--replace-imports-with-any django.utils.functional \
	--replace-imports-with-any django.utils.html \
	--replace-imports-with-any django.utils.safestring \
	--replace-imports-with-any django.utils.text \
	--replace-imports-with-any django.views \
	--replace-imports-with-any django.views.decorators.csrf \
	--replace-imports-with-any django.views.decorators.http \
	--replace-imports-with-any wagtail \
	--replace-imports-with-any wagtail.admin.forms.models \
	--replace-imports-with-any wagtail.admin.panels \
	--replace-imports-with-any wagtail.admin.ui.tables \
	--replace-imports-with-any wagtail.admin.views \
	--replace-imports-with-any wagtail.admin.viewsets.model \
	--replace-imports-with-any wagtail.blocks \
	--replace-imports-with-any wagtail.blocks.stream_block \
	--replace-imports-with-any wagtail.contrib.settings.models \
	--replace-imports-with-any wagtail.fields \
	--replace-imports-with-any wagtail.images.blocks \
	--replace-imports-with-any wagtail.images.widgets \
	--replace-imports-with-any wagtail.models \
	--replace-imports-with-any wagtail.permissions \
	--replace-imports-with-any wagtail.signals \
	--replace-imports-with-any wagtail.snippets.action_menu \
	--replace-imports-with-any wagtail.snippets.blocks \
	--replace-imports-with-any wagtail.snippets.models \
	--replace-imports-with-any wagtail.snippets.permissions \
	--replace-imports-with-any wagtail.snippets.views.chooser \
	--replace-imports-with-any wagtail.snippets.views.snippets
PYREFLY_IGNORES = \
	--ignore missing-attribute \
	--ignore bad-override \
	--ignore not-callable

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
	$(MAKE) typecheck
	black --check --config pyproject.toml core cli tests
	isort --settings-path pyproject.toml --check-only core cli tests

typecheck: ## Run targeted Pyrefly type checking
	pyrefly check \
		--search-path core \
		--search-path cli \
		$(PYREFLY_REPLACE_IMPORTS) \
		$(PYREFLY_IGNORES) \
		seeders/ \
		core/sum_core/blocks/ \
		core/sum_core/forms/ \
		core/sum_core/leads/ \
		core/sum_core/navigation/ \
		core/sum_core/branding/ \
		cli/sum_cli/commands/ \
		--project-excludes '**/migrations/*' \
		--project-excludes '**/test_project/*'

lint-strict: lint

format: ## Auto-format code
	black --config pyproject.toml core cli tests
	isort --settings-path pyproject.toml core cli tests


test: ## Run fast tests (default, excludes slow/integration)
	python -m pytest

test-integration: ## Run integration/slow tests only
	python -m pytest -m "slow or integration"

test-full: ## Run all tests except E2E
	python -m pytest -m "" --ignore=tests/e2e

test-e2e: ## Run Playwright E2E tests
	python -m pytest tests/e2e

test-cli: ## Run CLI test slice only
	python -m pytest cli/tests -q

test-themes: ## Run themes test slice only
	python -m pytest tests/themes -q

test-templates: ## Run template loading order tests (fast gate)
	python -m pytest tests/templates/test_template_loading_order.py -q

test-fast: ## Run high-signal test slices (CLI + themes)
	python -m pytest cli/tests tests/themes -q

verify-source-intact: ## Verify tests did not modify protected repo paths
	bash scripts/verify_source_intact.sh

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

preflight: ## Run preflight sync against origin/develop
	./scripts/codex_preflight.sh
