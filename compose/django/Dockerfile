ARG ENVIRONMENT=local

# Base image
FROM python:3.12-slim-bookworm AS python


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# BUILD STAGE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
FROM python AS python-build-stage

ARG ENVIRONMENT

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# UV configuration
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12

WORKDIR /app

# Install dependencies (caching layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
      # Use the frozen lock file
      --frozen \
      # Don't include dev dependencies
      $([ "$ENVIRONMENT" = "local" ] && echo "" || echo "--no-dev") \
      # Don't install the project
      --no-install-project

ADD . /app

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen $([ "$ENVIRONMENT" = "local" ] && echo "" || echo "--no-dev")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# RUNTIME STAGE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
FROM python AS python-runtime-stage

ARG ENVIRONMENT

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=${ENVIRONMENT}

WORKDIR /app

# Create non-root user
RUN addgroup --system django \
  && adduser --system --ingroup django django

# Copy application and scripts with proper permissions
COPY --from=python-build-stage --chown=django:django /app /app
COPY --chown=django:django ./compose/django/start /start

# Create staticfiles directory with correct ownership and permissions
RUN mkdir -p /app/staticfiles && chown django:django /app/staticfiles && chmod 755 /app/staticfiles

# Prepare scripts
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Switch to `django` user
USER django
