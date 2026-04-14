from abc import ABC, abstractmethod

from common.types import SongCreate, SongEntity


class SongStore(ABC):
    @abstractmethod
    def store(self, song_create: SongCreate) -> SongEntity: ...
