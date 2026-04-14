from pydantic import BaseModel, ConfigDict, Field, field_validator


class RatingCreate(BaseModel):
    song_id: str
    rating: int = Field(ge=1, le=5)


class RatingEntity(RatingCreate):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v: object) -> str:
        return str(v)


class RatingStats(BaseModel):
    avg: float
    lowest: int
    highest: int
