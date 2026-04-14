from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from adapters.document_stores.document_db.common import MongoDBClientCommon
from adapters.document_stores.song_store import SongStore
from common.types import SongCreate, SongEntity


class MongoSongStore(SongStore, MongoDBClientCommon):
    COLLECTION = "song"

    @property
    def collection(self) -> Collection:
        return self.db[self.COLLECTION]

    @staticmethod
    def _to_dto(song: dict) -> SongEntity:
        return SongEntity(
            _id=str(song["_id"]),
            artist=song["artist"],
            title=song["title"],
            difficulty=song["difficulty"],
            level=song["level"],
            released=song["released"],
        )

    def store(self, song_create: SongCreate) -> SongEntity:
        data = song_create.model_dump()
        inserted_id = self.collection.insert_one(data).inserted_id
        return SongEntity(_id=str(inserted_id), **song_create.model_dump())

    def find_all(self, page_size: int, last_id: str | None = None) -> list[SongEntity]:
        query = {"_id": {"$gt": ObjectId(last_id)}} if last_id else {}
        songs = self.collection.find(query).limit(page_size)
        return [self._to_dto(s) for s in songs]

    def find_by_id(self, song_id: str) -> SongEntity | None:
        try:
            song = self.collection.find_one({"_id": ObjectId(song_id)})
        except InvalidId:
            return None
        return self._to_dto(song) if song else None

    def avg_difficulty(self, level: int | None = None) -> float | None:
        match_stage = (
            {"$match": {"level": level}} if level is not None else {"$match": {}}
        )
        pipeline = [
            match_stage,
            {"$group": {"_id": None, "avg": {"$avg": "$difficulty"}}},
        ]
        result = list(self.collection.aggregate(pipeline))  # type: ignore[arg-type]
        return result[0]["avg"] if result else None

    def search(self, message: str) -> list[SongEntity]:
        songs = self.collection.find(
            {"$text": {"$search": message}},
            {"score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})])
        return [self._to_dto(s) for s in songs]
