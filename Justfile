# Start containers
up *args: lint
    docker compose up {{ args }}


# Stop & remove containers
down *args:
    docker compose down {{ args }}


# Re-build containers
build *args:
    docker compose build {{ args }}


# Execute command in running container
exec *args:
    docker compose exec {{ args }}


# Create temporary container & run command
run *args:
    docker compose run -T --rm {{ args }}


# Show logs from container(s)
logs *args:
    docker compose logs {{ args }}


# Create new Alembic migration
makemigrations MESSAGE="auto":
    docker compose run -T --rm fastapi alembic revision --autogenerate -m "{{ MESSAGE }}"


# Apply Alembic migrations
migrate:
    docker compose run -T --rm fastapi alembic upgrade head


# Format and check code
lint:
    uv tool run ruff format .
    uv tool run ruff check . --fix
