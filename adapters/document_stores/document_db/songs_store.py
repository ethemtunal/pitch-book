from abc import ABC, abstractmethod

from adapters.document_stores.document_db.common import MongoDBClientCommon
from common.types import SongCreate, SongEntity


class SongStore(ABC):
    @abstractmethod
    def store(self, song_create: SongCreate) -> SongEntity: ...


class MongoSongStore(SongStore, MongoDBClientCommon):
    COLLECTION = "song"

    @property
    def collection(self):
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
        song = self.collection.find_one({"_id": inserted_id})
        return self._to_dto(song)
