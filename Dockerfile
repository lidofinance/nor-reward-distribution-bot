FROM python:3.12.15-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"

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

FROM base AS production

RUN apt-get update && apt-get install -y --no-install-recommends -qq \
    curl=8.14.1-2+deb13u7 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /app
COPY interfaces ./interfaces
COPY src ./src

# Build metadata for the startup log and the build_info metric. The Harbor workflow passes these as build args;
# regenerate build-info.json from them. Local builds without the args keep the tracked "unknown" placeholders.
ARG BUILD_VERSION
ARG BUILD_BRANCH
ARG BUILD_COMMIT
COPY build-info.json ./
RUN if [ -n "$BUILD_COMMIT" ]; then \
      printf '{"version":"%s","branch":"%s","commit":"%s"}\n' \
        "$BUILD_VERSION" "$BUILD_BRANCH" "$BUILD_COMMIT" > build-info.json; \
    fi \
 && chown -R www-data /app/

ENV PROMETHEUS_PORT=9000
ENV HEALTHCHECK_SERVER_HOST=0.0.0.0
ENV HEALTHCHECK_SERVER_PORT=9010

EXPOSE $PROMETHEUS_PORT $HEALTHCHECK_SERVER_PORT
USER www-data

HEALTHCHECK --interval=10s --timeout=3s \
    CMD ["sh", "-c", "curl -f http://localhost:$HEALTHCHECK_SERVER_PORT/healthcheck || exit 1"]

ENTRYPOINT ["python3", "src/main.py"]
