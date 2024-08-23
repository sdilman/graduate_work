.PHONY: env, up_service, up_test_f, up_test_i, down, clean


env:
	@cp deploy-app/.env.example deploy-app/.env
	@cp deploy-test-functional/.env.example deploy-test-functional/.env
	@cp deploy-test-integration/.env.example deploy-test-integration/.env

up_service: env
	@docker compose -f deploy-app/docker-compose.yml up --build

up_test_f: env
	@docker compose -f deploy-test-functional/docker-compose.yml up --build

up_test_i: env
	@docker compose -f deploy-test-integration/docker-compose.yml up --build

down:
	- docker compose -f deploy-app/docker-compose.yml down -v
	- docker compose -f deploy-test-functional/docker-compose.yml down -v
	- docker compose -f deploy-test-functional/docker-compose.yml down -v

clean: down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true