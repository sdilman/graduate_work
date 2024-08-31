.PHONY: env
env:
	@find services -name ".env.example" | while read file; do \
		cp "$$file" "$$(dirname $$file)/.env"; \
	done

.PHONY: up_all
up_all: env
	@docker compose -f docker-compose.yml up --build

.PHONY: up_service
up_service: env
	@docker compose -f services/billing/docker-compose.yml up --build

.PHONY: up_test_f
up_test_f: env
	@docker compose -f services/billing/tests/functional/docker-compose.yml up --build

.PHONY: up_test_i
up_test_i: env
	@docker compose -f services/billing/tests/integration/docker-compose.yml up --build

.PHONY: down
down:
	@find services -name "docker-compose.yml" | while read file; do \
		docker compose -f "$$file" down -v || true; \
	done

.PHONY: clean
clean: down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true
	- docker images -q | xargs -r docker rmi || true


.PHONY: sync
sync:
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@uv venv
	@uv sync --frozen --all-extras

.PHONY: activate
activate:
	@SHELL_PATH=$$($$SHELL -c 'echo $$SHELL') && . .venv/bin/activate && exec $$SHELL_PATH

.PHONY: pre-commit
pre-commit:
	@pre-commit install

.PHONY: setup
setup: sync activate pre-commit

.PHONY: check
check:
	@git add .
	@pre-commit run
