# -- General
SHELL := /bin/bash

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_RUN          = $(COMPOSE) run --rm

# -- Moodle
HOOK_MOODLE_TAG      ?= v4.1.5
HOOK_MOODLE_GIT      ?= git://git.moodle.org/moodle.git

default: help

# ======================================================================================
# FILES / DIRECTORIES
# ======================================================================================

data/moodle/html:
	mkdir -p data/moodle/html
	git clone --depth 1 --branch $(HOOK_MOODLE_TAG) $(HOOK_MOODLE_GIT) data/moodle/html

data/moodle/moodledata:
	mkdir -p data/moodle/moodledata

# ======================================================================================
# RULES
# ======================================================================================

clean: ## remove local files
	rm -rf data
.PHONY: clean

build: ## build the moodle container
build: \
	data/moodle/html \
	data/moodle/moodledata
	$(COMPOSE) build moodle
.PHONY: build

down: ## remove containers, volumes and images
	@$(COMPOSE) down --rmi all -v --remove-orphans
.PHONY: down

logs: ## display moodle logs (follow mode)
	@$(COMPOSE) logs -f moodle
.PHONY: logs

run: ## run the moodle container
	@$(COMPOSE) up -d moodle
.PHONY: run

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop containers
	@$(COMPOSE) stop
.PHONY: stop

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
