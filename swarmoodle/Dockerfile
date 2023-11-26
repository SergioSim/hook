# -- Base image --
FROM python:3.11-slim as base

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install tini && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

WORKDIR /app

# Copy all sources
COPY . /app/

# Install swarmoodle
RUN pip install -e .[dev]

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}

ENTRYPOINT ["/usr/bin/tini-static", "--"]
CMD [ "locust" ]
