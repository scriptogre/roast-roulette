# Default command
default: up


# Start app
up *args:
    #!/usr/bin/env sh

    # Setup Tailwind CSS CLI
    just setup-tailwindcss-cli

    trap 'kill 0' EXIT

    # Start Django
    docker compose up &

    # Start Tailwind CSS CLI
    # ./tailwindcss -i ./main/static/css/input.css -o ./main/static/css/output.css --watch --minify

    # Open browser
    (sleep 2 && uv run -m webbrowser http://localhost:8000)

    wait


# Run `python manage.py makemigrations`
makemigrations *args:
    docker compose run --rm django python manage.py makemigrations {{ args }}


# Run `python manage.py migrate`
migrate:
    docker compose run --rm django python manage.py migrate


# Run `{cmd}` in django container
exec +cmd:
    docker compose run --rm django {{ cmd }}


# Destroy containers & volumes
destroy:
    docker compose down --volumes


# Tailwind CSS CLI setup
setup-tailwindcss-cli:
    #!/usr/bin/env bash

    if [ -f "./tailwindcss" ] || [ -f "./tailwindcss.exe" ]; then
        echo "Tailwind CSS CLI is already installed."
        exit 0
    fi

    TAILWIND_VERSION="4.0.1"
    BASE_URL="https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}"
    echo "Select your operating system and architecture:"
    echo "1) Linux (ARM64)"
    echo "2) Linux (ARMv7)"
    echo "3) Linux (x64)"
    echo "4) macOS (ARM64)"
    echo "5) macOS (x64)"
    echo "6) Windows (ARM64)"
    echo "7) Windows (x64)"
    read -p "Enter the number corresponding to your system: " choice
    case "$choice" in
        1) ARCH="linux-arm64" ;;
        2) ARCH="linux-armv7" ;;
        3) ARCH="linux-x64" ;;
        4) ARCH="macos-arm64" ;;
        5) ARCH="macos-x64" ;;
        6) ARCH="windows-arm64" ;;
        7) ARCH="windows-x64" ;;
        *) echo "Invalid choice. Exiting."; exit 1 ;;
    esac
    BINARY="tailwindcss-$ARCH"
    if [[ "$ARCH" == windows-* ]]; then
        BINARY="$BINARY.exe"
    fi
    DOWNLOAD_URL="$BASE_URL/$BINARY"
    OUTPUT_FILE="./tailwindcss"
    if [[ "$ARCH" == windows-* ]]; then
        OUTPUT_FILE="$OUTPUT_FILE.exe"
    fi
    echo "Downloading Tailwind CSS CLI for $ARCH..."
    curl -L -o "$OUTPUT_FILE" "$DOWNLOAD_URL"
    if [[ "$ARCH" != windows-* ]]; then
        chmod +x "$OUTPUT_FILE"
    fi
    echo "Tailwind CSS CLI has been downloaded to $OUTPUT_FILE"
