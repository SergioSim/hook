# -- General
SHELL := /bin/bash

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID                   = $(shell id -u)
DOCKER_GID                   = $(shell id -g)
DOCKER_USER                  = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE                      = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_RUN                  = $(COMPOSE) run --rm

# -- Moodle
HOOK_MOODLE_TAG              ?= v4.1.5
HOOK_MOODLE_GIT              ?= git://git.moodle.org/moodle.git
HOOK_MOODLE_ADMIN_PASSWORD   ?= password
HOOK_MOODLE_ADMIN_EMAIL      ?= admin@example.com
HOOK_MOODLE_SITE_NAME        ?= Hook

HOOK_MOODLE_DEMOCOURSE_1     ?= https://moodle.net/.pkg/@moodlenet/ed-resource/dl/ed-resource/uHFOlHUh/063_PFB1.mbz

default: help

# ======================================================================================
# FILES / DIRECTORIES
# ======================================================================================

data/moodle/html:
	mkdir -p data/moodle/html
	git clone --depth 1 --branch $(HOOK_MOODLE_TAG) $(HOOK_MOODLE_GIT) data/moodle/html

data/moodle/html/config.php:
	cp config/moodle/config.php data/moodle/html/config.php

data/moodle/html/demo_course_1.mbz:
	@$(COMPOSE_RUN) curl $(HOOK_MOODLE_DEMOCOURSE_1) -o /var/www/html/demo_course_1.mbz

data/moodle/moodledata:
	mkdir -p data/moodle/moodledata

# ======================================================================================
# RULES
# ======================================================================================

clean: ## remove local files
	rm -rf data
.PHONY: clean

bootstrap: ## ## bootstrap the project for development
bootstrap: \
	build \
	migrate \
	run
.PHONY: bootstrap

build: ## build the moodle container
build: \
	data/moodle/html \
	data/moodle/moodledata \
	data/moodle/html/config.php \
	data/moodle/html/demo_course_1.mbz
	$(COMPOSE) build moodle
.PHONY: build

down: ## remove containers, volumes and images
	@$(COMPOSE) down -v --remove-orphans #--rmi all
.PHONY: down

logs: ## display moodle logs (follow mode)
	@$(COMPOSE) logs -f moodle
.PHONY: logs

migrate:  ## run moodle database migrations
	@$(COMPOSE) up -d mysql
	@$(COMPOSE_RUN) dockerize -wait tcp://mysql:3306 -timeout 60s
	@$(COMPOSE_RUN) moodle php admin/cli/install_database.php \
		--agree-license \
		--fullname=$(HOOK_MOODLE_SITE_NAME) \
		--shortname=$(HOOK_MOODLE_SITE_NAME) \
		--adminpass=$(HOOK_MOODLE_ADMIN_PASSWORD) \
		--adminemail=$(HOOK_MOODLE_ADMIN_EMAIL) \
		|| true
	@$(COMPOSE_RUN) moodle php admin/cli/restore_backup.php \
		--file=/var/www/html/demo_course_1.mbz \
		--categoryid=1 \
		|| true
.PHONY: migrate

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
