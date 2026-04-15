# pitch-book

A REST API for songs and ratings built with Python 3, Flask, and MongoDB.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [just](https://github.com/casey/just)
- Docker

## Running the app

```bash
just up
```

This starts MongoDB and the API via Docker Compose. The API will be available at `http://localhost:8000`.
On first startup the database is seeded automatically with the songs from `data/songs.json`.

To stop:

```bash
just down
```

## Running the tests

```bash
just test-env
uv run pytest
```

`just test-env` starts a local MongoDB container. Tests clean up after themselves.

## Database

### Indexes

Indexes are created automatically on app startup via `init_db()` (called from `create_app()`):

- `song.artist` + `song.title` compound text index, required for `$text` search
- `song.level` speeds up average difficulty queries filtered by level
- `rating.song_id` speeds up rating stats aggregation per song

### Seeding

On startup, `main.py` calls `seed_db()` which loads `data/songs.json` into the `song` collection if it is empty. Each song is validated through Pydantic before insertion, ensuring consistent data types in the database.

For tests, seeding is intentionally skipped each test starts with an empty collection and cleans up after itself.

## Data validation

All request bodies are validated with [Pydantic](https://docs.pydantic.dev/) before hitting the database. Invalid requests return a `422` with details.

## Tests

The test suite covers three layers:

- **Models** Pydantic validation rules (boundary values, rejection of invalid input)
- **Stores** MongoDB operations (find, paginate, aggregate, search) against a real database
- **Endpoints** all routes tested via Flask test client including error cases (400, 404, 422)

```bash
just test-env
uv run pytest
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/songs/` | List songs (cursor-based pagination via `page_size` and `last_id`) |
| `GET` | `/songs/avg/difficulty` | Average difficulty, optional `level` filter |
| `GET` | `/songs/search?message=` | Search songs by artist or title |
| `POST` | `/songs/rating` | Add a rating (1–5) for a song |
| `GET` | `/songs/rating/<song_id>` | Get avg, lowest, and highest rating for a song |

### List songs
```bash
curl http://localhost:8000/songs/
curl "http://localhost:8000/songs/?page_size=5&last_id=<last_id>"
```

### Average difficulty
```bash
curl http://localhost:8000/songs/avg/difficulty
curl "http://localhost:8000/songs/avg/difficulty?level=9"
```

### Search songs
```bash
curl "http://localhost:8000/songs/search?message=Yousicians"
```

### Add a rating
```bash
curl -X POST http://localhost:8000/songs/rating \
  -H "Content-Type: application/json" \
  -d '{"song_id": "<song_id>", "rating": 4}'
```

### Get rating stats
```bash
curl http://localhost:8000/songs/rating/<song_id>
```
