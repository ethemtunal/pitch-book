from abc import ABC, abstractmethod

from adapters.document_stores.document_db.rates_store import RatingStore
from adapters.document_stores.document_db.songs_store import SongStore


class DocumentStore(ABC):
    @property
    @abstractmethod
    def song(self) -> SongStore: ...

    @property
    @abstractmethod
    def rating(self) -> RatingStore: ...
