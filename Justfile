set dotenv-load := true   # Load .env file


# Based on COMPOSE_FILE, Dispatches to 'dev' for local development or 'up --detach' in production
default: start


start *args:
    #!/usr/bin/env sh
    case "$COMPOSE_FILE" in
      docker-compose.local.yml)
        exec just dev "$@"
        ;;
      docker-compose.production.yml)
        exec just up --detach "$@"
        ;;
      *)
        echo >&2 "Error: Set COMPOSE_FILE in .env to either 'docker-compose.local.yml' or 'docker-compose.production.yml'"
        exit 1
        ;;
    esac


# Start Docker services & TailwindCSS CLI in watch mode
dev *args:
    #!/usr/bin/env sh
    # Kill all child processes on exit
    trap 'kill 0' EXIT
    # Start the web server
    docker compose up {{ args }} &
    # Start the Tailwind CSS CLI
    just tailwindcss &
    # Wait for all processes to finish
    wait


# Start containers
up *args:
    docker compose up {{ args }}


# Stop & remove containers
down:
    docker compose down --remove-orphans


# Rebuild docker images
build:
    docker compose build --no-cache


# Stop & remove containers + volumes
destroy:
    #!/usr/bin/env bash
    if [ "$COMPOSE_FILE" = "docker-compose.production.yml" ]; then
        echo "Warning: You are about to destroy production data. Are you sure? (y/N)"
        read -r confirm
        if [ "$confirm" != "y" ]; then
            echo "Aborted."
            exit 1
        fi
    fi
    docker compose down --remove-orphans --volumes


# Run `python manage.py makemigrations`
makemigrations *args:
    docker compose run --rm django python manage.py makemigrations {{ args }}


# Run `python manage.py migrate`
migrate:
    docker compose run --rm django python manage.py migrate


# Run `{cmd}` in django container
exec +cmd:
    docker compose run --rm django {{ cmd }}


# Run TailwindCSS CLI in watch mode
tailwindcss: download-tailwindcss
    ./tailwindcss -i ./main/static/css/input.css -o ./main/static/css/output.css --watch=always


# Download Standalone CLI binary for TailwindCSS. Auto-detects OS and architecture.
download-tailwindcss:
    #!/usr/bin/env bash

    [ -f "./tailwindcss" ] && echo "TailwindCSS Standalone CLI is already downloaded." && exit 0

    TAILWIND_VERSION="4.1.4"
    BASE_URL="https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}"

    OS=$(uname -s)
    ARCH=$(uname -m)
    case "$OS" in
        Linux*)  case "$ARCH" in x86_64) ARCH="linux-x64" ;; aarch64) ARCH="linux-arm64" ;; armv7l) ARCH="linux-armv7" ;; *) echo "Unsupported architecture: $ARCH"; exit 1 ;; esac ;;
        Darwin*) case "$ARCH" in x86_64) ARCH="macos-x64" ;; arm64) ARCH="macos-arm64" ;; *) echo "Unsupported architecture: $ARCH"; exit 1 ;; esac ;;
        *) echo "Unsupported OS: $OS"; exit 1 ;;
    esac

    BINARY="tailwindcss-$ARCH"
    OUTPUT_FILE="./tailwindcss"

    echo "Downloading TailwindCSS Standalone CLI for $ARCH..."
    curl -L -o "$OUTPUT_FILE" "$BASE_URL/$BINARY" && chmod +x "$OUTPUT_FILE"
    echo "TailwindCSS Standalone CLI has been downloaded to $OUTPUT_FILE"
