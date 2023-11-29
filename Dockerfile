# -- Base image --
FROM python:3.11-slim as base

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Upgrade system packages to install security updates
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y openjdk-17-jre && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -- Development --
FROM base as development

# Copy all sources
COPY . /app/

# Install Hook
RUN pip install -e .[dev]

# Un-privileged user running the application
RUN useradd -m -s /bin/bash --uid ${DOCKER_USER:-1000} hook
USER hook
