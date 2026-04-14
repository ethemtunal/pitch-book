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
    docker run --name="pitch-book-test-mongodb-$(date +%s)" \
      -e MONGO_INITDB_ROOT_USERNAME=pitch-book \
      -e MONGO_INITDB_ROOT_PASSWORD=dbpasswd \
      -e MONGO_INITDB_DATABASE=pitch-book-document-db \
      -p 27017:27017 \
      -d mongo:8.0.4 || true

stop-test-container:
    docker stop $(docker ps -a -q --filter="name=pitch-book-test-mongodb") || true

rm-test-container:
    docker rm $(docker ps -a -q --filter="name=pitch-book-test-mongodb") || true

test-env:
    just stop-test-container rm-test-container test-container
