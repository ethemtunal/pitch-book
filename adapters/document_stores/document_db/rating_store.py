from pymongo.collection import Collection

from adapters.document_stores.document_db.common import MongoDBClientCommon
from adapters.document_stores.rating_store import RatingStore
from common.types import RatingCreate, RatingEntity, RatingStats


class MongoRatingStore(RatingStore, MongoDBClientCommon):
    COLLECTION = "rating"

    @property
    def collection(self) -> Collection:
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
        return RatingEntity(_id=str(inserted_id), **rating_create.model_dump())

    def get_stats(self, song_id: str) -> RatingStats | None:
        pipeline = [
            {"$match": {"song_id": song_id}},
            {
                "$group": {
                    "_id": None,
                    "avg": {"$avg": "$rating"},
                    "lowest": {"$min": "$rating"},
                    "highest": {"$max": "$rating"},
                }
            },
        ]
        result = list(self.collection.aggregate(pipeline))  # type: ignore[arg-type]
        if not result:
            return None
        return RatingStats(
            avg=result[0]["avg"],
            lowest=result[0]["lowest"],
            highest=result[0]["highest"],
        )
