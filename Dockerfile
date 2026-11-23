FROM dhi.io/python:3.12.16-debian13-dev@sha256:fcf859cfc756541f139b1d14951d838c4d119fece09734f12968ddf94801f8ad AS builder

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV POETRY_VERSION=1.8.2
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Build metadata for the startup log and the build_info metric. The release workflow passes these as build args;
# regenerate build-info.json from them. Local builds without the args keep the tracked "unknown" placeholders.
# This runs here because the runtime image has no shell.
WORKDIR /meta
ARG BUILD_VERSION
ARG BUILD_BRANCH
ARG BUILD_COMMIT
COPY build-info.json ./
RUN if [ -n "$BUILD_COMMIT" ]; then \
      printf '{"version":"%s","branch":"%s","commit":"%s"}\n' \
        "$BUILD_VERSION" "$BUILD_BRANCH" "$BUILD_COMMIT" > build-info.json; \
    fi

FROM dhi.io/python:3.12.16-debian13@sha256:d730c81938acce56e361f94829e4979a542ada9195e54b32347478743147b5ac AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VENV_PATH="/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /app
COPY interfaces ./interfaces
COPY src ./src
COPY --from=builder /meta/build-info.json ./

ENV PROMETHEUS_PORT=9000
ENV HEALTHCHECK_SERVER_HOST=0.0.0.0
ENV HEALTHCHECK_SERVER_PORT=9010

EXPOSE $PROMETHEUS_PORT $HEALTHCHECK_SERVER_PORT

HEALTHCHECK --interval=10s --timeout=3s \
    CMD ["python3", "src/healthcheck.py"]

ENTRYPOINT ["python3", "src/main.py"]
