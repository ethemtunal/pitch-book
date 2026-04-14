from abc import ABC, abstractmethod

from common.types import RatingCreate, RatingEntity, RatingStats


class RatingStore(ABC):
    @abstractmethod
    def store(self, rating_create: RatingCreate) -> RatingEntity: ...

    @abstractmethod
    def get_stats(self, song_id: str) -> RatingStats | None: ...
