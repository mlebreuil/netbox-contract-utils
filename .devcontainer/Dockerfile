FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Major version of the PostgreSQL server (see POSTGRES_VERSION in docker-compose.yml).
# pg_dump / psql must be at least as recent as the server, and Debian's own
# postgresql-client is older than the server image, so install it from PGDG.
ARG PG_VERSION=17

ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq \
    && apt-get install --yes -qq --no-install-recommends postgresql-common \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
    # Build dependencies NetBox needs (see the NetBox installation guide)
    && apt-get install --yes -qq --no-install-recommends \
      postgresql-client-${PG_VERSION} \
      libpq-dev \
      libxml2-dev \
      libxslt1-dev \
      libffi-dev \
      libssl-dev \
      zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp
