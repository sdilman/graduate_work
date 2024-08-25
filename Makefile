.PHONY: env
env:
	@cp services/billing/.env.example services/billing/.env
	@cp services/billing/tests/functional/.env.example services/billing/tests/functional/.env
	@cp services/billing/tests/integration/.env.example services/billing/tests/integration/.env

.PHONY: up_service
up_service: env
	@docker compose -f services/billing/docker-compose.yml up --build

.PHONY: up_test_f
up_test_f: env
	@docker services/billing/tests/functional/docker-compose.yml up --build

.PHONY: up_test_i
up_test_i: env
	@docker compose -f services/billing/tests/integration/docker-compose.yml up --build

.PHONY: down
down:
	- docker compose -f services/billing/docker-compose.yml down -v || true
	- docker compose -f services/billing/tests/functional/docker-compose.yml down -v  || true
	- docker compose -f services/billing/tests/integration/docker-compose.yml down -v  || true

.PHONY: clean
clean: down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true
	- docker images -q | xargs -r docker rmi || true

.PHONY: setup_precommit
setup_precommit:
	@pre-commit install
