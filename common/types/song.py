from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.types.serialized import SerializedDate


class SongCreate(BaseModel):
    artist: str
    title: str
    difficulty: float
    level: int
    released: SerializedDate


class SongEntity(SongCreate):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v: object) -> str:
        return str(v)
