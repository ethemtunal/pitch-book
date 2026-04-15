import json
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC
from pathlib import Path

from pymongo import ASCENDING, TEXT, MongoClient
from pymongo.synchronous.client_session import ClientSession

from adapters.document_stores.document_db.rating_store import MongoRatingStore
from adapters.document_stores.document_db.song_store import MongoSongStore
from adapters.document_stores.document_store import DocumentStore
from adapters.document_stores.rating_store import RatingStore
from adapters.document_stores.song_store import SongStore
from common.configuration import Config
from common.types import SongCreate


class DocumentDBDocumentStore(DocumentStore):
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
        self._song_store: SongStore | None = None
        self._rating_store: RatingStore | None = None

    @property
    def song(self) -> SongStore:
        if self._song_store is None:
            self._song_store = MongoSongStore(
                client_session=self.client_session,
            )
        return self._song_store

    @property
    def rating(self) -> RatingStore:
        if self._rating_store is None:
            self._rating_store = MongoRatingStore(
                client_session=self.client_session,
            )
        return self._rating_store


@contextmanager
def get_document_store_session(
    uri: str | None = None,
) -> Generator[ClientSession, None, None]:
    if not uri:
        uri = Config().document_db_uri
    client: MongoClient = MongoClient(uri, retryWrites=False, tz_aware=True, tzinfo=UTC)
    try:
        with client.start_session() as session:
            yield session
    except Exception:
        raise
    finally:
        client.close()


def get_document_store(client_session: ClientSession) -> DocumentDBDocumentStore:
    return DocumentDBDocumentStore(client_session=client_session)


def init_db(uri: str | None = None, db_name: str | None = None) -> None:
    config = Config()
    client: MongoClient = MongoClient(uri or config.document_db_uri)
    try:
        db = client[db_name or config.document_db_name]
        # required for text search
        db["song"].create_index([("artist", TEXT), ("title", TEXT)])
        # optimizing the level filtering on avg_difficulty
        db["song"].create_index([("level", ASCENDING)])
        # optimizing the song_id filter on get_stats
        db["rating"].create_index([("song_id", ASCENDING)])

    finally:
        client.close()


def seed_db(uri: str | None = None, db_name: str | None = None) -> None:
    config = Config()
    client: MongoClient = MongoClient(uri or config.document_db_uri)
    try:
        db = client[db_name or config.document_db_name]
        if db["song"].count_documents({}) == 0:
            songs_path = Path(__file__).resolve().parents[3] / "data" / "songs.json"
            songs = [
                SongCreate.model_validate(s).model_dump()
                for s in json.loads(songs_path.read_text())
            ]
            db["song"].insert_many(songs)
    finally:
        client.close()
