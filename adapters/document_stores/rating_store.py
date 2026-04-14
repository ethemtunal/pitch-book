from abc import ABC, abstractmethod

from common.types import RatingCreate, RatingEntity


class RatingStore(ABC):
    @abstractmethod
    def store(self, rating_create: RatingCreate) -> RatingEntity: ...
