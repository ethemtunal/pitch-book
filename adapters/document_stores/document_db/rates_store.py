from abc import ABC, abstractmethod

from adapters.document_stores.document_db.common import MongoDBClientCommon
from common.types import RatingCreate, RatingEntity


class RatingStore(ABC):
    @abstractmethod
    def store(self, rating_create: RatingCreate) -> RatingEntity: ...


class MongoRatingStore(RatingStore, MongoDBClientCommon):
    COLLECTION = "rating"

    @property
    def collection(self):
        return self.db[self.COLLECTION]

    @staticmethod
    def _to_dto(rating: dict) -> RatingEntity:
        return RatingEntity(
            _id=str(rating["_id"]),
            song_id=rating["song_id"],
            rating=rating["rating"],
        )

    def store(self, rating_create: RatingCreate) -> RatingEntity:
        data = rating_create.model_dump()
        inserted_id = self.collection.insert_one(data).inserted_id
        rating = self.collection.find_one({"_id": inserted_id})
        return self._to_dto(rating)
