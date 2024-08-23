.PHONY: env
env:
	@cp deploy-app/.env.example deploy-app/.env
	@cp deploy-test-functional/.env.example deploy-test-functional/.env
	@cp deploy-test-integration/.env.example deploy-test-integration/.env

.PHONY: up_service
up_service: env
	@docker compose -f deploy-app/docker-compose.yml up --build

.PHONY: up_test_f
up_test_f: env
	@docker compose -f deploy-test-functional/docker-compose.yml up --build

.PHONY: up_test_i
up_test_i: env
	@docker compose -f deploy-test-integration/docker-compose.yml up --build

.PHONY: down
down:
	- docker compose -f deploy-app/docker-compose.yml down -v
	- docker compose -f deploy-test-functional/docker-compose.yml down -v
	- docker compose -f deploy-test-functional/docker-compose.yml down -v

.PHONY: clean
clean: down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true

.PHONY: setup_precommit
setup_precommit:
	@if [ -z "$$(command -v pip3)" ]; then \
		PIP_CMD="pip3"; \
	else \
		PIP_CMD="pip"; \
	fi; \
	$$PIP_CMD install --upgrade pip; \
	if [ -z "$$(command -v pre-commit)" ]; then \
		$$PIP_CMD install pre-commit pydantic mypy ruff; \
		pre-commit install; \
	else \
		$$PIP_CMD install --upgrade pre-commit pydantic mypy ruff; \
		pre-commit install; \
	fi
