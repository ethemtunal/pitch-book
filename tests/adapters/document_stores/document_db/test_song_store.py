from datetime import date

import pytest
from pymongo import TEXT

from adapters.document_stores.document_db.song_store import MongoSongStore
from common.types import SongCreate


@pytest.fixture
def store(document_db_session):
    s = MongoSongStore(client_session=document_db_session)
    s.collection.create_index([("artist", TEXT), ("title", TEXT)])
    return s


@pytest.fixture
def sample_song() -> SongCreate:
    return SongCreate(
        artist="The Yousicians",
        title="Lycanthropic Metamorphosis",
        difficulty=14.6,
        level=13,
        released=date(2016, 10, 26),
    )


class TestFindAll:
    def test_returns_all_songs(self, store, sample_song):
        store.store(sample_song)
        store.store(sample_song)

        result = store.find_all(page_size=10)

        assert len(result) == 2

    def test_respects_page_size(self, store, sample_song):
        for _ in range(5):
            store.store(sample_song)

        result = store.find_all(page_size=3)

        assert len(result) == 3

    def test_cursor_pagination_returns_next_page(self, store, sample_song):
        for _ in range(5):
            store.store(sample_song)

        first_page = store.find_all(page_size=3)
        second_page = store.find_all(page_size=3, last_id=first_page[-1].id)

        assert len(second_page) == 2
        assert {s.id for s in first_page}.isdisjoint({s.id for s in second_page})

    def test_returns_empty_when_no_songs(self, store):
        result = store.find_all(page_size=10)

        assert result == []

    def test_returns_empty_for_invalid_last_id(self, store, sample_song):
        store.store(sample_song)

        result = store.find_all(page_size=10, last_id="not-a-valid-id")

        assert result == []


class TestFindById:
    def test_store_and_find_by_id(self, store, sample_song):
        stored = store.store(sample_song)

        result = store.find_by_id(stored.id)

        assert result is not None
        assert result.id == stored.id
        assert result.artist == stored.artist
        assert result.title == stored.title

    def test_returns_none_for_unknown_id(self, store):
        result = store.find_by_id("000000000000000000000000")

        assert result is None

    def test_returns_none_for_invalid_id(self, store):
        result = store.find_by_id("not-a-valid-id")

        assert result is None


class TestAvgDifficulty:
    def test_returns_average_across_all_songs(self, store):
        store.store(
            SongCreate(
                artist="A",
                title="T",
                difficulty=10.0,
                level=5,
                released=date(2020, 1, 1),
            )
        )
        store.store(
            SongCreate(
                artist="A",
                title="T",
                difficulty=20.0,
                level=5,
                released=date(2020, 1, 1),
            )
        )

        result = store.avg_difficulty()

        assert result == 15.0

    def test_filters_by_level(self, store):
        store.store(
            SongCreate(
                artist="A",
                title="T",
                difficulty=10.0,
                level=5,
                released=date(2020, 1, 1),
            )
        )
        store.store(
            SongCreate(
                artist="A",
                title="T",
                difficulty=20.0,
                level=9,
                released=date(2020, 1, 1),
            )
        )

        result = store.avg_difficulty(level=5)

        assert result == 10.0

    def test_returns_none_when_no_songs(self, store):
        result = store.avg_difficulty()

        assert result is None

    def test_returns_none_when_level_has_no_songs(self, store, sample_song):
        store.store(sample_song)

        result = store.avg_difficulty(level=99)

        assert result is None


class TestSearch:
    def test_matches_by_title(self, store, sample_song):
        store.store(sample_song)

        result = store.search("Lycanthropic")

        assert len(result) == 1
        assert result[0].title == sample_song.title

    def test_matches_by_artist(self, store, sample_song):
        store.store(sample_song)

        result = store.search("Yousicians")

        assert len(result) == 1
        assert result[0].artist == sample_song.artist

    def test_is_case_insensitive(self, store, sample_song):
        store.store(sample_song)

        result = store.search("lycanthropic")

        assert len(result) == 1

    def test_returns_empty_for_no_match(self, store, sample_song):
        store.store(sample_song)

        result = store.search("nonexistent")

        assert result == []
