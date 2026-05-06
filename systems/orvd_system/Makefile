.PHONY: help prepare unit-test integration-test tests docker-test docker-up docker-down docker-logs

GENERATED = .generated
DOCKER = /c/Program\ Files/Docker/Docker/resources/bin/docker.exe
DOCKER_NETWORK ?= orvd_drones_net
DOCKER_COMPOSE = DOCKER_NETWORK=$(DOCKER_NETWORK) $(DOCKER) compose -f $(GENERATED)/docker-compose.yml --env-file $(GENERATED)/.env
VENV_PYTHON = ../../.venv/Scripts/python.exe
PROFILE ?= kafka

ifeq ($(wildcard $(VENV_PYTHON)),$(VENV_PYTHON))
PYTHON = $(VENV_PYTHON)
ROOT_PYTHON = .venv/Scripts/python.exe
else
PYTHON ?= python
ROOT_PYTHON = $(PYTHON)
endif

PYTEST = $(PYTHON) -m pytest -p no:cacheprovider

help:
	@echo "make prepare           - Собрать docker-compose + .env из компонентов"
	@echo "make docker-up         - Запустить систему (prepare + docker compose up)"
	@echo "make docker-down       - Остановить систему"
	@echo "make docker-logs       - Логи"
	@echo "make unit-test         - Unit тесты"
	@echo "make integration-test  - Интеграционные тесты (без docker)"
	@echo "make docker-test       - Интеграционные тесты (docker)"
	@echo "make tests             - Все тесты"

# ---------------------------------------------------------------------------
# DOCKER
# ---------------------------------------------------------------------------

prepare:
	@cd ../.. && PYTHONUTF8=1 $(ROOT_PYTHON) scripts/prepare_system.py systems/orvd_system

docker-up: prepare
	@$(DOCKER_COMPOSE) --profile $(PROFILE) up -d --build

docker-down:
	@$(DOCKER_COMPOSE) --profile $(PROFILE) down

docker-logs:
	@$(DOCKER_COMPOSE) --profile $(PROFILE) logs -f

# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

unit-test:
	@echo "=== Unit тесты ==="
	@$(PYTEST) tests/unit/ -v --tb=short

integration-test:
	@echo "=== Интеграционные тесты (in-process) ==="
	@$(PYTEST) tests/integration/ -v --tb=short

docker-test: docker-up
	@echo "=== Docker smoke test ==="
	@$(DOCKER_COMPOSE) ps

tests: unit-test integration-test
	@echo ""
	@echo "Все тесты пройдены."
