from tests.api.conftest import SAMPLE_SONG


class TestAddSong:
    def test_returns_201_with_created_song(self, client):
        response = client.post("/songs/", json=SAMPLE_SONG)

        assert response.status_code == 201
        data = response.get_json()
        assert data["artist"] == SAMPLE_SONG["artist"]
        assert data["title"] == SAMPLE_SONG["title"]
        assert "id" in data

    def test_returns_422_on_missing_field(self, client):
        body = {k: v for k, v in SAMPLE_SONG.items() if k != "artist"}

        response = client.post("/songs/", json=body)

        assert response.status_code == 422

    def test_returns_422_on_invalid_type(self, client):
        body = {**SAMPLE_SONG, "difficulty": "not-a-number"}

        response = client.post("/songs/", json=body)

        assert response.status_code == 422


class TestGetSongs:
    def test_returns_200_with_songs(self, client):
        client.post("/songs/", json=SAMPLE_SONG)

        response = client.get("/songs/")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == SAMPLE_SONG["title"]

    def test_returns_empty_list_when_no_songs(self, client):
        response = client.get("/songs/")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_respects_page_size(self, client):
        for _ in range(5):
            client.post("/songs/", json=SAMPLE_SONG)

        response = client.get("/songs/?page_size=3")

        assert response.status_code == 200
        assert len(response.get_json()) == 3

    def test_cursor_pagination_with_last_id(self, client):
        for _ in range(5):
            client.post("/songs/", json=SAMPLE_SONG)

        first_page = client.get("/songs/?page_size=3").get_json()
        last_id = first_page[-1]["id"]

        second_page = client.get(f"/songs/?page_size=3&last_id={last_id}").get_json()

        assert len(second_page) == 2
        first_ids = {s["id"] for s in first_page}
        assert all(s["id"] not in first_ids for s in second_page)


class TestAvgDifficulty:
    def test_returns_average_difficulty(self, client):
        client.post("/songs/", json={**SAMPLE_SONG, "difficulty": 10.0, "level": 5})
        client.post("/songs/", json={**SAMPLE_SONG, "difficulty": 20.0, "level": 5})

        response = client.get("/songs/avg/difficulty")

        assert response.status_code == 200
        assert response.get_json()["average"] == 15.0

    def test_filters_by_level(self, client):
        client.post("/songs/", json={**SAMPLE_SONG, "difficulty": 10.0, "level": 5})
        client.post("/songs/", json={**SAMPLE_SONG, "difficulty": 20.0, "level": 9})

        response = client.get("/songs/avg/difficulty?level=5")

        assert response.status_code == 200
        assert response.get_json()["average"] == 10.0

    def test_returns_null_when_no_songs(self, client):
        response = client.get("/songs/avg/difficulty")

        assert response.status_code == 200
        assert response.get_json()["average"] is None


class TestSearchSongs:
    def test_returns_400_when_message_missing(self, client):
        response = client.get("/songs/search")

        assert response.status_code == 400

    def test_returns_matching_songs_by_title(self, client):
        client.post("/songs/", json=SAMPLE_SONG)

        response = client.get("/songs/search?message=Lycanthropic")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["title"] == SAMPLE_SONG["title"]

    def test_returns_matching_songs_by_artist(self, client):
        client.post("/songs/", json=SAMPLE_SONG)

        response = client.get("/songs/search?message=Yousicians")

        assert response.status_code == 200
        assert len(response.get_json()) == 1

    def test_returns_empty_for_no_match(self, client):
        client.post("/songs/", json=SAMPLE_SONG)

        response = client.get("/songs/search?message=nonexistent")

        assert response.status_code == 200
        assert response.get_json() == []


class TestAddRating:
    def test_returns_201_on_valid_rating(self, client):
        song = client.post("/songs/", json=SAMPLE_SONG).get_json()

        response = client.post(
            "/songs/rating", json={"song_id": song["id"], "rating": 4}
        )

        assert response.status_code == 201

    def test_returns_404_for_unknown_song(self, client):
        response = client.post(
            "/songs/rating",
            json={"song_id": "000000000000000000000000", "rating": 3},
        )

        assert response.status_code == 404

    def test_returns_422_when_rating_out_of_range(self, client):
        song = client.post("/songs/", json=SAMPLE_SONG).get_json()

        response = client.post(
            "/songs/rating", json={"song_id": song["id"], "rating": 6}
        )

        assert response.status_code == 422

    def test_returns_422_on_missing_field(self, client):
        response = client.post("/songs/rating", json={"rating": 3})

        assert response.status_code == 422


class TestGetRatingStats:
    def test_returns_stats_for_rated_song(self, client):
        song = client.post("/songs/", json=SAMPLE_SONG).get_json()
        client.post("/songs/rating", json={"song_id": song["id"], "rating": 2})
        client.post("/songs/rating", json={"song_id": song["id"], "rating": 4})

        response = client.get(f"/songs/rating/{song['id']}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["avg"] == 3.0
        assert data["lowest"] == 2
        assert data["highest"] == 4

    def test_returns_404_when_no_ratings(self, client):
        song = client.post("/songs/", json=SAMPLE_SONG).get_json()

        response = client.get(f"/songs/rating/{song['id']}")

        assert response.status_code == 404

    def test_returns_404_for_unknown_song(self, client):
        response = client.get("/songs/rating/000000000000000000000000")

        assert response.status_code == 404
