import pytest

from api.app import create_app


@pytest.fixture
def client(document_db_session):
    """
    Flask test client wired to the same MongoDB instance used by document_db_session,
    so the post-test collection drop in that fixture cleans up API-written data too.
    """
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as c:
        yield c


SAMPLE_SONG = {
    "artist": "The Yousicians",
    "title": "Lycanthropic Metamorphosis",
    "difficulty": 14.6,
    "level": 13,
    "released": "2016-10-26",
}
