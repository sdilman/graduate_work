ONESHELL:

TEST-COMPOSE-FILE=.temp-docker-compose.yml

define temp_compose_up
	printf "include:\n- docker/docker-compose.yml\n-$(1)" > $(TEST-COMPOSE-FILE) && \
	docker compose -f $(TEST-COMPOSE-FILE) up --build
endef

define temp_interg_compose_up
	printf "include:\n- docker/docker-compose.yml\n-$(1)\n-$(2)" > $(TEST-COMPOSE-FILE) && \
	docker compose -f $(TEST-COMPOSE-FILE) up --build
endef


.PHONY: env
env:
	@find services -name ".env.example" | while read file; do \
		cp "$$file" "$$(dirname $$file)/.env"; \
	done

.PHONY: up_all
up_all: env
	@docker compose -f docker-compose.yml up --build

.PHONY: up_auth
up_auth: env
	$(call temp_compose_up, services/auth/docker-compose.yml)

.PHONY: up_auth_test_func
up_auth_test_func: env
	$(call temp_compose_up, services/auth/tests/functional/docker-compose.yml)

.PHONY: up_bill
up_bill: env
	$(call temp_compose_up, services/billing/docker-compose.yml)

.PHONY: up_bill_test_func
up_bill_test_func: env
	$(call temp_compose_up, services/billing/tests/functional/docker-compose.yml)

.PHONY: up_bill_test_integr
up_bill_test_integr: env
	$(call temp_interg_compose_up, services/billing/tests/integration/docker-compose.yml, services/auth/docker-compose.yml)

.PHONY: down
down:
	@docker compose down -v

.PHONY: clean
clean: down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true
	- docker images -q | xargs -r docker rmi || true
	- rm .*temp*.yml || true

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
	@pre-commit clean
	@pre-commit install --install-hooks

.PHONY: update-pythonpath
update-pythonpath:
	export PYTHONPATH=$(find $(pwd)/services -type d -name "src" | paste -sd ":" -)

.PHONY: setup
setup: sync activate pre-commit

.PHONY: check
check:
	@git add .
	@pre-commit run
