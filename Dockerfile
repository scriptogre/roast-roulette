# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# BUILD STAGE: Install dependencies
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the existing system interpreter across both images.
ENV UV_PYTHON_DOWNLOADS=0

# Install the venv in /usr/local (rather than app's /code) to fix issues during bind mounts
ENV UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /code

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /code

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# RUNTIME STAGE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
FROM python:3.13-slim-bookworm

# Create non-root user matching host UID:GID
ARG UID=1000
ARG GID=1000
RUN addgroup --gid $GID non-root && \
    adduser --uid $UID --gid $GID --disabled-password --gecos '' non-root

# Copy venv & app from builder
COPY --from=builder --chown=$UID:$GID /usr/local /usr/local
COPY --from=builder --chown=$UID:$GID /code /code

WORKDIR /code

ENV PATH="/usr/local/bin:${PATH}" PYTHONPATH="/code" PYTHONUNBUFFERED=1

# Create data/, and media/ dirs
RUN mkdir -p ./data && chown non-root:non-root ./data
RUN mkdir -p ./media && chown non-root:non-root ./media

# Switch to `non-root` user
USER non-root

CMD ["fastapi", "run", "main/app.py"]

EXPOSE 8000
