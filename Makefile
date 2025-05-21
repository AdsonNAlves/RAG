.PHONY: up down logs exec restart
##########################
COMPOSE_FILE=podman-compose.yml
COMPOSE_FILE_PROD=podma-prod.yml ## não esta pronto
#########################
up:
	podman-compose -f $(COMPOSE_FILE) up -d --build

upprod:
	podman-compose -f $(COMPOSE_FILE_PROD) up -d --build

down:
	podman-compose -f $(COMPOSE_FILE) down

downprod:
	podman-compose -f $(COMPOSE_FILE_PROD) down

logs:
	podman-compose -f $(COMPOSE_FILE) logs -f rag-app

exec:
	podman exec -it rag_app bash

restart:
	make down && make up

# Ambiente de desenvolvimento
dev:
	@echo "Iniciando ambiente de desenvolvimento..."
	make up

# Ambiente de produção (pode customizar se houver compose.prod.yml no futuro)
prod:
	@echo "Iniciando ambiente de produção..."
	make upprod
