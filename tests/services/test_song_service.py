from datetime import date

import pytest
from pymongo import TEXT

from common.exceptions import NotFound
from common.types import SongCreate
from services.song_service import SongService


@pytest.fixture
def service(document_store) -> SongService:
    document_store.song.collection.create_index([("artist", TEXT), ("title", TEXT)])
    return SongService(document_store=document_store)


@pytest.fixture
def sample_song() -> SongCreate:
    return SongCreate(
        artist="The Yousicians",
        title="Lycanthropic Metamorphosis",
        difficulty=14.6,
        level=13,
        released=date(2016, 10, 26),
    )


class TestAddSong:
    def test_stores_and_returns_song(self, service, sample_song):
        result = service.add_song(sample_song)

        assert result.id is not None
        assert result.artist == sample_song.artist
        assert result.title == sample_song.title


class TestGetSongs:
    def test_returns_stored_songs(self, service, sample_song):
        service.add_song(sample_song)
        service.add_song(sample_song)

        result = service.get_songs(page_size=10)

        assert len(result) == 2

    def test_paginates_with_last_id(self, service, sample_song):
        for _ in range(5):
            service.add_song(sample_song)

        first_page = service.get_songs(page_size=3)
        second_page = service.get_songs(page_size=3, last_id=first_page[-1].id)

        assert len(second_page) == 2


class TestGetAvgDifficulty:
    def test_returns_avg_difficulty(self, service, sample_song):
        service.add_song(sample_song)

        result = service.get_avg_difficulty()

        assert result == sample_song.difficulty

    def test_filters_by_level(self, service):
        service.add_song(
            SongCreate(
                artist="A",
                title="T",
                difficulty=10.0,
                level=5,
                released=date(2020, 1, 1),
            )
        )
        service.add_song(
            SongCreate(
                artist="A",
                title="T",
                difficulty=20.0,
                level=9,
                released=date(2020, 1, 1),
            )
        )

        result = service.get_avg_difficulty(level=5)

        assert result == 10.0


class TestSearchSongs:
    def test_returns_matching_songs(self, service, sample_song):
        service.add_song(sample_song)

        result = service.search_songs("Yousicians")

        assert len(result) == 1
        assert result[0].artist == sample_song.artist


class TestAddRating:
    def test_stores_rating_for_existing_song(self, service, sample_song):
        song = service.add_song(sample_song)

        service.add_rating(song_id=song.id, rating=4)

        stats = service.get_rating_stats(song.id)
        assert stats is not None
        assert stats.avg == 4.0

    def test_raises_not_found_for_unknown_song(self, service):
        with pytest.raises(NotFound):
            service.add_rating(song_id="000000000000000000000000", rating=4)


class TestGetRatingStats:
    def test_returns_stats(self, service, sample_song):
        song = service.add_song(sample_song)
        service.add_rating(song_id=song.id, rating=3)
        service.add_rating(song_id=song.id, rating=5)

        result = service.get_rating_stats(song.id)

        assert result is not None
        assert result.avg == 4.0
        assert result.lowest == 3
        assert result.highest == 5

    def test_raises_not_found_for_unknown_song(self, service):
        with pytest.raises(NotFound):
            service.get_rating_stats("000000000000000000000000")
