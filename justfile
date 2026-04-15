default:
    @just --list

format:
    ruff check --select I --fix ./
    ruff format ./

fix:
    just format
    ruff check --fix

check:
    just fix
    mypy .

test-container:
    docker run --detach --name songs_db \
      --publish 127.0.0.1:27017:27017 \
      mongo:7.0 || true

stop-test-container:
    docker stop songs_db || true

rm-test-container:
    docker rm songs_db || true

test-env:
    just stop-test-container rm-test-container test-container

up:
    just stop-test-container rm-test-container
    docker compose up --build

down:
    docker compose down -v
