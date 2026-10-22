# python:3.12-slim on Debian 13 (trixie), pinned by the multi-arch index digest.
# Update the digest together with the apt package versions below.
FROM python:3.12-slim@sha256:cb33f7f771ecec2ef1225cf39b159591a040391bd73e4c01f00fdfc4c47611d2 AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"

# Build stage: the compiler and headers are needed only to install the dependencies.
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends -qq \
    libffi-dev=3.4.8-2 \
    g++=4:14.2.0-1 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Runtime stage: the virtualenv from the builder, the application code and curl for the health check.
FROM base AS production

# Passed by the CI build workflow; defaults keep local builds working.
ARG BUILD_VERSION=unknown
ARG BUILD_BRANCH=unknown
ARG BUILD_COMMIT=unknown

RUN apt-get update && apt-get install -y --no-install-recommends -qq \
    curl=8.14.1-2+deb13u7 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /app
COPY interfaces ./interfaces
COPY src ./src

RUN printf '{"version":"%s","branch":"%s","commit":"%s","buildTime":"%s"}\n' \
      "$BUILD_VERSION" "$BUILD_BRANCH" "$BUILD_COMMIT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /app/build-info.json \
 && chown -R www-data /app/

ENV PROMETHEUS_PORT=9000
ENV HEALTHCHECK_SERVER_HOST=0.0.0.0
ENV HEALTHCHECK_SERVER_PORT=9010

EXPOSE $PROMETHEUS_PORT $HEALTHCHECK_SERVER_PORT
USER www-data

HEALTHCHECK --interval=10s --timeout=3s \
    CMD ["sh", "-c", "curl -f http://localhost:$HEALTHCHECK_SERVER_PORT/healthcheck || exit 1"]

ENTRYPOINT ["python3", "src/main.py"]
