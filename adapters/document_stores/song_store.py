from abc import ABC, abstractmethod

from common.types import SongCreate, SongEntity


class SongStore(ABC):
    @abstractmethod
    def store(self, song_create: SongCreate) -> SongEntity: ...

    @abstractmethod
    def find_all(
        self, page_size: int, last_id: str | None = None
    ) -> list[SongEntity]: ...

    @abstractmethod
    def find_by_id(self, song_id: str) -> SongEntity | None: ...

    @abstractmethod
    def avg_difficulty(self, level: int | None = None) -> float | None: ...

    @abstractmethod
    def search(self, message: str) -> list[SongEntity]: ...
