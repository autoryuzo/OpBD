.PHONY: help prepare orvd-unit-test noflyzones-unit-test unit-test integration-test test-all-docker tests docker-up docker-down docker-logs

PIPENV_PIPFILE = ../../config/Pipfile
PYTEST_CONFIG = ../../config/pyproject.toml
GENERATED = .generated
DOCKER_COMPOSE = docker compose -f $(GENERATED)/docker-compose.yml --env-file $(GENERATED)/.env

PIPENV = PIPENV_PIPFILE=$(PIPENV_PIPFILE) pipenv
PYTEST = cd ../.. && $(PIPENV) run pytest -c config/pyproject.toml

help:
	@echo "make prepare           - Собрать docker-compose + .env из компонентов"
	@echo "make docker-up         - Запустить систему (prepare + docker compose up)"
	@echo "make docker-down       - Остановить систему"
	@echo "make docker-logs       - Логи"
	@echo "make orvd-unit-test    - Unit тесты ORVD и gateway"
	@echo "make noflyzones-unit-test - Unit тесты компонента запретных зон"
	@echo "make unit-test         - Все unit тесты системы"
	@echo "make integration-test  - Интеграционные тесты (без docker)"
	@echo "make test-all-docker   - Подготовка и запуск docker-системы"
	@echo "make tests             - Все in-process тесты"

# ---------------------------------------------------------------------------
# DOCKER
# ---------------------------------------------------------------------------

prepare:
	@cd ../.. && PIPENV_PIPFILE=config/Pipfile pipenv run python scripts/prepare_system.py systems/orvd_system

docker-up: prepare
	@set -a && . $(GENERATED)/.env && set +a && \
		profiles="--profile $${BROKER_TYPE:-kafka}"; \
		[ "$${ENABLE_ELK:-false}" = "true" ] && profiles="$$profiles --profile elk"; \
		[ "$${ENABLE_FABRIC:-false}" = "true" ] && profiles="$$profiles --profile fabric"; \
		$(DOCKER_COMPOSE) $$profiles up -d --build

docker-down:
	@set -a && . $(GENERATED)/.env && set +a && \
		profiles="--profile $${BROKER_TYPE:-kafka}"; \
		[ "$${ENABLE_ELK:-false}" = "true" ] && profiles="$$profiles --profile elk"; \
		[ "$${ENABLE_FABRIC:-false}" = "true" ] && profiles="$$profiles --profile fabric"; \
		$(DOCKER_COMPOSE) $$profiles down 2>/dev/null || true

docker-logs:
	@set -a && . $(GENERATED)/.env && set +a && \
		profiles="--profile $${BROKER_TYPE:-kafka}"; \
		[ "$${ENABLE_ELK:-false}" = "true" ] && profiles="$$profiles --profile elk"; \
		[ "$${ENABLE_FABRIC:-false}" = "true" ] && profiles="$$profiles --profile fabric"; \
		$(DOCKER_COMPOSE) $$profiles logs -f

# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

orvd-unit-test:
	@echo "=== Unit тесты ORVD и gateway ==="
	@$(PYTEST) orvd_system/tests/unit/test_orvd_unit.py -v --tb=short

noflyzones-unit-test:
	@echo "=== Unit тесты компонента запретных зон ==="
	@$(PYTEST) orvd_system/tests/unit/test_noflyzones_unit.py -v --tb=short

unit-test:
	@echo "=== Unit тесты ==="
	@$(PYTEST) orvd_system/tests/unit/ -v --tb=short

integration-test:
	@echo "=== Интеграционные тесты (in-process) ==="
	@$(PYTEST) orvd_system/tests/integration/ -v --tb=short

test-all-docker: docker-up
	@echo "Docker-система запущена. Используйте make docker-logs для просмотра логов."

tests: unit-test integration-test
	@echo ""
	@echo "Все тесты пройдены."
