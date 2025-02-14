# Get environment as build arg (from docker-compose.yml, defaults to 'local')
ARG ENVIRONMENT=local

FROM python:3.12.7-slim-bookworm AS builder

ARG ENVIRONMENT

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# Optimize UV
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies (caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
      --frozen \
      --no-install-project \
      # Map "local" to "dev" group, keep "production" as-is
      --group $(if [ "$ENVIRONMENT" = "local" ]; then echo "dev"; else echo "$ENVIRONMENT"; fi)

COPY . /app

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
      --frozen \
      --group $(if [ "$ENVIRONMENT" = "local" ]; then echo "dev"; else echo "$ENVIRONMENT"; fi)


# Final stage
FROM python:3.12.7-slim-bookworm

ARG ENVIRONMENT

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy application and scripts
COPY --from=builder /app /app
COPY ./compose/django/start /start

# Prepare scripts
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Create non-root `django` user
RUN addgroup --system django  \
    && adduser --system --ingroup django django \
    && chown -R django:django /app /start

# Switch to `django` user
USER django

# Make environment available as env var (e.g. for /start script)
ENV ENVIRONMENT=${ENVIRONMENT}
