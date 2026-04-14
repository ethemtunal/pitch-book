from abc import ABC, abstractmethod

from adapters.document_stores.rates_store import RatingStore
from adapters.document_stores.songs_store import SongStore


class DocumentStore(ABC):
    @property
    @abstractmethod
    def song(self) -> SongStore: ...

    @property
    @abstractmethod
    def rating(self) -> RatingStore: ...
