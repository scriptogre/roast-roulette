# Note: COMPOSE_FILE must be set in .env file to run commands
set dotenv-load := true  # Load .env file


# Default command
default: dev


# Start app
dev *args:
    #!/usr/bin/env sh
    if [ "$COMPOSE_FILE" != "docker-compose.local.yml" ]; then
        echo "Error: The 'dev' command can only be run when COMPOSE_FILE is set to docker-compose.local.yml"
        exit 1
    fi

    # Kill all child processes on exit
    trap 'kill 0' EXIT

    # Start the Django server
    docker compose up {{ args }} &

    # Open the browser (after 4s)
    (sleep 4 && uv run -m webbrowser http://localhost:8000) &

    # Start the Tailwind CSS CLI
    just tailwindcss

    # Wait for all processes to finish
    wait


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
    ./tailwindcss -i ./main/static/css/input.css -o ./main/static/css/output.css --watch


# Download Standalone CLI binary for TailwindCSS. Auto-detects OS and architecture.
download-tailwindcss:
    #!/usr/bin/env bash

    [ -f "./tailwindcss" ] && echo "TailwindCSS Standalone CLI is already downloaded." && exit 0

    TAILWIND_VERSION="4.0.9"
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
