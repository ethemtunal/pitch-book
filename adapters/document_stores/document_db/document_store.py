import logging
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC

from pymongo import MongoClient
from pymongo.synchronous.client_session import ClientSession

from adapters.document_stores.document_db.rates_store import (
    MongoRatingStore,
    RatingStore,
)
from adapters.document_stores.document_db.songs_store import MongoSongStore, SongStore
from adapters.document_stores.document_store import DocumentStore
from common.configuration import Config

logging.getLogger("pymongo.client").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class DocumentDBDocumentStore(DocumentStore):
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
        self._song_store: SongStore | None = None
        self._rate_store: RatingStore | None = None

    @property
    def song(self) -> SongStore:
        if self._song_store is None:
            self._song_store = MongoSongStore(
                client_session=self.client_session,
            )
        return self._song_store

    @property
    def rating(self) -> RatingStore:
        if self._rate_store is None:
            self._rate_store = MongoRatingStore(
                client_session=self.client_session,
            )
        return self._rate_store


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
