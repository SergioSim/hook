# -- General
SHELL := /bin/bash

# -- Moodle
HOOK_MOODLE_ADMIN_EMAIL         ?= admin@example.com
HOOK_MOODLE_ADMIN_PASSWORD      ?= password
HOOK_MOODLE_DEMOCOURSE_1        ?= https://moodle.net/.pkg/@moodlenet/ed-resource/dl/ed-resource/uHFOlHUh/063_PFB1.mbz
HOOK_MOODLE_DEMOCOURSE_2        ?= https://moodle.net/.pkg/@moodlenet/ed-resource/dl/ed-resource/ow9swOdh/352_DL2023backup_moodle2_course_66_digital_literacy_20230627_1204_nu.mbz
HOOK_MOODLE_DEMOCOURSE_3        ?= https://moodle.net/.pkg/@moodlenet/ed-resource/dl/ed-resource/QTQj2Z0m/278_Applied_English.mbz
HOOK_MOODLE_GIT                 ?= git://git.moodle.org/moodle.git
HOOK_MOODLE_PLUGIN_LOGSTORE_GIT ?= https://github.com/xAPI-vle/moodle-logstore_xapi.git
HOOK_MOODLE_PLUGIN_LOGSTORE_TAG ?= v4.7.0
HOOK_MOODLE_SITE_NAME           ?= Hook
HOOK_MOODLE_TAG                 ?= v4.1.5

# -- MySQL
HOOK_MOODLE_MYSQL_DATABASE       ?= moodle
HOOK_MOODLE_MYSQL_PASSWORD       ?= password
HOOK_MOODLE_MYSQL_ROOT_PASSWORD  ?= password
HOOK_MOODLE_MYSQL_USER           ?= moodle

# -- Ralph
HOOK_RALPH_ELASTICSEARCH_INDEX    ?= statements
HOOK_RALPH_ELASTICSEARCH_PORT     ?= 9200
HOOK_RALPH_LRS_AUTH_USER_NAME     ?= ralph
HOOK_RALPH_LRS_AUTH_USER_PASSWORD ?= password
HOOK_RALPH_LRS_AUTH_USER_SCOPE    ?= all
HOOK_RALPH_URL                    ?= http://ralph

# -- Hook
HOOK_API_PORT                        ?= 8000
HOOK_MOODLE_URL                      ?= http://moodle
HOOK_MOODLE_WEBSERVICE_TOKEN         ?= 32323232323232323232323232323232
HOOK_MOODLE_WEBSERVICE_PRIVATE_TOKEN ?= 6464646464646464646464646464646464646464646464646464646464646464

# -- Kafka
HOOK_KAFKA_TOPIC             ?= statements
HOOK_KAFKA_BOOTSTRAP_SERVERS ?= kafka:9092

# -- Spark
HOOK_SPARK_MASTER_URL          ?= spark://spark-master:7077
HOOK_SPARK_MASTER_WEB_UI_PORT  ?= 8090
HOOK_SPARK_WORKERS             ?= 1

# -- Swarmoodle
HOOK_SWARMOODLE_LOCUST_SPAWN_RATE             ?= 50
HOOK_SWARMOODLE_MOODLE_COURSE_ID              ?= 2
HOOK_SWARMOODLE_MOODLE_DELETE_USERS_AFTER_RUN ?= 0
HOOK_SWARMOODLE_MOODLE_STUDENTS               ?= 1
HOOK_SWARMOODLE_OULAD_CODE_MODULE             ?= AAA
HOOK_SWARMOODLE_OULAD_CODE_PRESENTATION       ?= 2013J
HOOK_SWARMOODLE_REQUEST_MILLISECONDS_DURATION ?= 400
HOOK_SWARMOODLE_SIMULATE_FIXED_DAY_DURATION   ?= 0

# -- OULAD
HOOK_KEEP_OULAD        ?= "false"
HOOK_OULAD_DATASET_URL ?= https://analyse.kmi.open.ac.uk/open_dataset/download

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID   = $(shell id -u)
DOCKER_GID   = $(shell id -g)
DOCKER_USER  = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE      = DOCKER_USER="$(DOCKER_USER)" \
			   HOOK_API_PORT="${HOOK_API_PORT}" \
			   HOOK_MAILPIT_UI_PORT="${HOOK_MAILPIT_UI_PORT}" \
			   HOOK_MOODLE_APACHE_PORT="$(HOOK_MOODLE_APACHE_PORT)" \
			   HOOK_MOODLE_MYSQL_DATABASE="${HOOK_MOODLE_MYSQL_DATABASE}" \
			   HOOK_MOODLE_MYSQL_PASSWORD="${HOOK_MOODLE_MYSQL_PASSWORD}" \
			   HOOK_MOODLE_MYSQL_ROOT_PASSWORD="${HOOK_MOODLE_MYSQL_ROOT_PASSWORD}" \
			   HOOK_MOODLE_MYSQL_USER="${HOOK_MOODLE_MYSQL_USER}" \
			   HOOK_MOODLE_URL="${HOOK_MOODLE_URL}" \
			   HOOK_MOODLE_WEBSERVICE_TOKEN="${HOOK_MOODLE_WEBSERVICE_TOKEN}" \
			   HOOK_SWARMOODLE_LOCUST_SPAWN_RATE="${HOOK_SWARMOODLE_LOCUST_SPAWN_RATE}" \
			   HOOK_SWARMOODLE_MOODLE_DELETE_USERS_AFTER_RUN="$(HOOK_SWARMOODLE_MOODLE_DELETE_USERS_AFTER_RUN)" \
			   HOOK_SWARMOODLE_MOODLE_COURSE_ID="$(HOOK_SWARMOODLE_MOODLE_COURSE_ID)" \
			   HOOK_SWARMOODLE_MOODLE_STUDENTS="$(HOOK_SWARMOODLE_MOODLE_STUDENTS)" \
			   HOOK_SWARMOODLE_OULAD_CODE_MODULE="$(HOOK_SWARMOODLE_OULAD_CODE_MODULE)" \
			   HOOK_SWARMOODLE_OULAD_CODE_PRESENTATION="$(HOOK_SWARMOODLE_OULAD_CODE_PRESENTATION)" \
			   HOOK_SWARMOODLE_REQUEST_MILLISECONDS_DURATION="$(HOOK_SWARMOODLE_REQUEST_MILLISECONDS_DURATION)" \
			   HOOK_SWARMOODLE_SIMULATE_FIXED_DAY_DURATION="$(HOOK_SWARMOODLE_SIMULATE_FIXED_DAY_DURATION)" \
			   HOOK_RALPH_ELASTICSEARCH_INDEX="${HOOK_RALPH_ELASTICSEARCH_INDEX}" \
			   HOOK_RALPH_ELASTICSEARCH_PORT="${HOOK_RALPH_ELASTICSEARCH_PORT}" \
			   HOOK_RALPH_LRS_AUTH_USER_NAME="${HOOK_RALPH_LRS_AUTH_USER_NAME}" \
			   HOOK_RALPH_LRS_AUTH_USER_PASSWORD="${HOOK_RALPH_LRS_AUTH_USER_PASSWORD}" \
			   HOOK_RALPH_URL="${HOOK_RALPH_URL}" \
			   HOOK_KAFKA_TOPIC="${HOOK_KAFKA_TOPIC}" \
			   HOOK_KAFKA_BOOTSTRAP_SERVERS="${HOOK_KAFKA_BOOTSTRAP_SERVERS}" \
			   HOOK_SPARK_MASTER_URL="${HOOK_SPARK_MASTER_URL}" \
			   HOOK_SPARK_MASTER_WEB_UI_PORT="${HOOK_SPARK_MASTER_WEB_UI_PORT}" \
			   HOOK_SPARK_WORKERS="${HOOK_SPARK_WORKERS}" \
               docker compose
COMPOSE_RUN  = $(COMPOSE) run --rm

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

data/moodle/html/demo_course_2.mbz:
	@$(COMPOSE_RUN) curl $(HOOK_MOODLE_DEMOCOURSE_2) -o /var/www/html/demo_course_2.mbz

data/moodle/html/demo_course_3.mbz:
	@$(COMPOSE_RUN) curl $(HOOK_MOODLE_DEMOCOURSE_3) -o /var/www/html/demo_course_3.mbz

data/moodle/html/admin/tool/log/store/xapi:
	mkdir -p data/moodle/html/admin/tool/log/store
	git clone \
		--depth 1 \
		--branch $(HOOK_MOODLE_PLUGIN_LOGSTORE_TAG) \
		$(HOOK_MOODLE_PLUGIN_LOGSTORE_GIT) \
		data/moodle/html/admin/tool/log/store/xapi

data/moodle/moodledata:
	mkdir -p data/moodle/moodledata

data/ralph/auth.json:
	mkdir -p data/ralph
	@$(COMPOSE_RUN) ralph ralph auth \
		-u $(HOOK_RALPH_LRS_AUTH_USER_NAME) \
		-p $(HOOK_RALPH_LRS_AUTH_USER_PASSWORD) \
		-s $(HOOK_RALPH_LRS_AUTH_USER_SCOPE) \
		-w

swarmoodle/data/OULAD:
	mkdir -p swarmoodle/data/OULAD
	wget -O swarmoodle/data/OULAD/dataset.zip $(HOOK_OULAD_DATASET_URL)
	unzip swarmoodle/data/OULAD/dataset.zip -d swarmoodle/data/OULAD
	rm swarmoodle/data/OULAD/dataset.zip

# ======================================================================================
# RULES
# ======================================================================================

clean: ## remove local files
	rm -rf data
	if [ "${HOOK_KEEP_OULAD}" = "false" ]; then \
        rm -rf swarmoodle/data/OULAD; \
	fi
.PHONY: clean

bootstrap: ## bootstrap the project for development
bootstrap: \
	build \
	migrate \
	run
.PHONY: bootstrap

build: ## build the hook and moodle containers
build: \
	data/moodle/html \
	data/moodle/moodledata \
	data/moodle/html/config.php \
	data/moodle/html/demo_course_1.mbz \
	data/moodle/html/demo_course_2.mbz \
	data/moodle/html/demo_course_3.mbz \
	data/moodle/html/admin/tool/log/store/xapi \
	data/ralph/auth.json \
	swarmoodle/data/OULAD
	$(COMPOSE) build hook moodle swarmoodle
.PHONY: build

down: ## remove containers, volumes and images
	@$(COMPOSE) down -v --remove-orphans #--rmi all
.PHONY: down

# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint python sources
lint: \
  lint-isort \
  lint-black \
  lint-flake8 \
  lint-pylint \
  lint-bandit \
  lint-pydocstyle
.PHONY: lint

lint-black: ## lint python sources with black
	@echo 'lint:black for hook started…'
	@$(COMPOSE_RUN) hook black hook tests
	@echo 'lint:black for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle black swarmoodle tests
.PHONY: lint-black

lint-flake8: ## lint python sources with flake8
	@echo 'lint:flake8 for hook started…'
	@$(COMPOSE_RUN) hook flake8 hook tests
	@echo 'lint:flake8 for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle flake8 swarmoodle tests
.PHONY: lint-flake8

lint-isort: ## automatically re-arrange python imports
	@echo 'lint:isort for hook started…'
	@$(COMPOSE_RUN) hook isort --atomic hook tests
	@echo 'lint:isort for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle isort --atomic swarmoodle tests
.PHONY: lint-isort

lint-pylint: ## lint python sources with pylint
	@echo 'lint:pylint for hook started…'
	@$(COMPOSE_RUN) hook pylint hook tests
	@echo 'lint:pylint for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle pylint swarmoodle tests
.PHONY: lint-pylint

lint-bandit: ## lint python sources with bandit
	@echo 'lint:bandit for hook started…'
	@$(COMPOSE_RUN) hook bandit -qr hook
	@echo 'lint:bandit for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle bandit -qr swarmoodle
.PHONY: lint-bandit

lint-pydocstyle: ## lint Python docstrings with pydocstyle
	@echo 'lint:pydocstyle for hook started…'
	@$(COMPOSE_RUN) hook pydocstyle hook tests
	@echo 'lint:pydocstyle for swarmoodle started…'
	@$(COMPOSE_RUN) swarmoodle pydocstyle swarmoodle tests
.PHONY: lint-pydocstyle

logs: ## display moodle logs (follow mode)
	@$(COMPOSE) logs -f
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
	HOOK_MOODLE_MYSQL_USER="$(HOOK_MOODLE_MYSQL_USER)" \
		HOOK_MOODLE_MYSQL_PASSWORD="$(HOOK_MOODLE_MYSQL_PASSWORD)" \
		HOOK_MOODLE_MYSQL_DATABASE="$(HOOK_MOODLE_MYSQL_DATABASE)" \
		HOOK_MOODLE_WEBSERVICE_TOKEN="$(HOOK_MOODLE_WEBSERVICE_TOKEN)" \
		HOOK_MOODLE_WEBSERVICE_PRIVATE_TOKEN="$(HOOK_MOODLE_WEBSERVICE_PRIVATE_TOKEN)" \
		 ./config/mysql/webservices.sh
	@$(COMPOSE_RUN) moodle php admin/cli/restore_backup.php \
		--file=/var/www/html/demo_course_1.mbz \
		--categoryid=1 \
		|| true
	@$(COMPOSE_RUN) moodle php admin/cli/restore_backup.php \
		--file=/var/www/html/demo_course_2.mbz \
		--categoryid=1 \
		|| true
	@$(COMPOSE_RUN) moodle php admin/cli/restore_backup.php \
		--file=/var/www/html/demo_course_3.mbz \
		--categoryid=1 \
		|| true

	@$(COMPOSE) up -d elasticsearch
	@$(COMPOSE_RUN) dockerize -wait tcp://elasticsearch:9200 -timeout 60s
	@$(COMPOSE_RUN) curl -X PUT http://elasticsearch:9200/$(HOOK_RALPH_ELASTICSEARCH_INDEX)
	@$(COMPOSE_RUN) curl -X PUT http://elasticsearch:9200/$(HOOK_RALPH_ELASTICSEARCH_INDEX)/_settings \
		-H 'Content-Type: application/json' \
		-d '{"index": {"number_of_replicas": 0}}'

	@$(COMPOSE_RUN) kafka kafka-topics.sh --create \
		--topic "${HOOK_KAFKA_TOPIC}" \
		--bootstrap-server "${HOOK_KAFKA_BOOTSTRAP_SERVERS}"
.PHONY: migrate

run: ## run the hook, moodle and spark containers
	@$(COMPOSE) up -d hook
.PHONY: run

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop containers
	@$(COMPOSE) stop
.PHONY: stop

swarmoodle:
	@$(COMPOSE_RUN) swarmoodle locust --skip-log-setup --headless --only-summary -f /app/swarmoodle
.PHONY: swarmoodle

test: ## run tests
test: \
	test-hook \
	test-swarmoodle
.PHONY: test

test-hook: ## run tests for hook
test-hook: run
	@$(COMPOSE_RUN) hook pytest
.PHONY: test-hook

test-swarmoodle: ## run tests for swarmoodle
test-swarmoodle: run
	@$(COMPOSE_RUN) swarmoodle pytest
.PHONY: test-swarmoodle

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
