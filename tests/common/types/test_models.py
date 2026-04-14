import pytest
from pydantic import ValidationError

from common.types import RatingCreate


class TestRatingCreate:
    def test_accepts_boundary_values(self):
        assert RatingCreate(song_id="x", rating=1).rating == 1
        assert RatingCreate(song_id="x", rating=5).rating == 5

    def test_rejects_rating_below_1(self):
        with pytest.raises(ValidationError):
            RatingCreate(song_id="x", rating=0)

    def test_rejects_rating_above_5(self):
        with pytest.raises(ValidationError):
            RatingCreate(song_id="x", rating=6)
