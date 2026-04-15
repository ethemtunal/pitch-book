from pymongo.client_session import ClientSession

from adapters.document_stores.document_db.document_store import get_document_store
from adapters.document_stores.document_store import DocumentStore
from common.exceptions import NotFound
from common.types import RatingCreate, RatingStats, SongCreate, SongEntity


class SongService:
    def __init__(self, document_store: DocumentStore) -> None:
        self.document_store = document_store

    def add_song(self, song: SongCreate) -> SongEntity:
        return self.document_store.song.store(song)

    def get_songs(self, page_size: int, last_id: str | None = None) -> list[SongEntity]:
        return self.document_store.song.find_all(page_size, last_id)

    def get_avg_difficulty(self, level: int | None = None) -> float | None:
        return self.document_store.song.avg_difficulty(level)

    def search_songs(self, message: str) -> list[SongEntity]:
        return self.document_store.song.search(message)

    def add_rating(self, song_id: str, rating: int) -> None:
        if not self.document_store.song.find_by_id(song_id):
            raise NotFound(f"Song {song_id} not found")
        self.document_store.rating.store(RatingCreate(song_id=song_id, rating=rating))

    def get_rating_stats(self, song_id: str) -> RatingStats:
        stats = self.document_store.rating.get_stats(song_id)
        if not stats:
            raise NotFound(f"No ratings found for song {song_id}")
        return stats


def get_song_service(document_store_session: ClientSession) -> SongService:
    return SongService(
        document_store=get_document_store(document_store_session),
    )
