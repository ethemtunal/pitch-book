import pytest

from adapters.document_stores.document_db.rating_store import MongoRatingStore
from common.types import RatingCreate


@pytest.fixture
def store(document_db_session) -> MongoRatingStore:
    return MongoRatingStore(client_session=document_db_session)


@pytest.fixture
def sample_rating() -> RatingCreate:
    return RatingCreate(song_id="abc123", rating=4)


class TestStore:
    def test_returns_entity_with_id(self, store, sample_rating):
        entity = store.store(sample_rating)

        assert entity.id is not None
        assert entity.song_id == sample_rating.song_id
        assert entity.rating == sample_rating.rating

    def test_persists_rating_to_db(self, store, sample_rating):
        entity = store.store(sample_rating)
        stats = store.get_stats(entity.song_id)

        assert stats is not None
        assert stats.avg == sample_rating.rating
        assert stats.lowest == sample_rating.rating
        assert stats.highest == sample_rating.rating


class TestGetStats:
    def test_returns_correct_avg(self, store):
        store.store(RatingCreate(song_id="song1", rating=2))
        store.store(RatingCreate(song_id="song1", rating=4))

        stats = store.get_stats("song1")

        assert stats is not None
        assert stats.avg == 3.0

    def test_returns_correct_lowest_and_highest(self, store):
        store.store(RatingCreate(song_id="song1", rating=1))
        store.store(RatingCreate(song_id="song1", rating=3))
        store.store(RatingCreate(song_id="song1", rating=5))
        store.store(RatingCreate(song_id="song1", rating=3))

        stats = store.get_stats("song1")

        assert stats is not None
        assert stats.lowest == 1
        assert stats.highest == 5
        assert stats.avg == 3

    def test_only_includes_ratings_for_given_song(self, store):
        store.store(RatingCreate(song_id="song1", rating=5))
        store.store(RatingCreate(song_id="song2", rating=1))

        stats = store.get_stats("song1")

        assert stats is not None
        assert stats.avg == 5.0
        assert stats.lowest == 5
        assert stats.highest == 5

    def test_returns_none_when_no_ratings(self, store):
        result = store.get_stats("nonexistent")

        assert result is None
