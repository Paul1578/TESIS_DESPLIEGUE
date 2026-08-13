# Mayan EDMS - stack Docker
# Uso (dentro del servidor o local, sin depender de SSH manual):
#   make up | make down | make deploy | make logs ...
# `make login` se hace UNA sola vez por servidor (o cuando caduque el token).

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help build up down stop restart status ps logs pull login deploy clean

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

build: ## Construye la imagen local con los parches y levanta
	$(COMPOSE) up -d --build

up: ## Levanta los contenedores
	$(COMPOSE) up -d

down: ## Detiene y borra contenedores (NO borra datos)
	$(COMPOSE) down

stop: ## Detiene los contenedores (los deja creados)
	$(COMPOSE) stop

restart: down up ## Reinicia el stack

status: ps ## Alias de ps

ps: ## Estado de los contenedores
	$(COMPOSE) ps

logs: ## Logs en vivo de la app
	$(COMPOSE) logs -f --tail=100 app

pull: ## Baja la ultima imagen de GHCR
	$(COMPOSE) pull

login: ## Login a GHCR (te pide el PAT). Se hace una sola vez por servidor
	docker login ghcr.io

deploy: ## Sincroniza repo, baja la imagen nueva y levanta (lo que hace el pipeline)
	git pull --ff-only
	$(COMPOSE) pull
	$(COMPOSE) up -d
	$(COMPOSE) image prune -f

clean: ## Elimina contenedores Y VOLUMENES (borra documentos y BD). CUIDADO
	$(COMPOSE) down -v
