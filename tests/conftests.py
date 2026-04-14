from datetime import UTC

import pytest
from pymongo import MongoClient

from adapters.document_stores.document_db.document_store import (
    DocumentStore,
    get_document_store,
)
from common.configuration import Config


@pytest.fixture(scope="function")
def document_db_session(integration_testconf):
    config = Config()
    client = MongoClient(
        config.document_db_uri, retryWrites=False, tz_aware=True, tzinfo=UTC
    )
    document_db = client[config.document_db_name]

    with client.start_session() as session:
        yield session

    for collection_name in document_db.list_collection_names():
        document_db[collection_name].drop()


@pytest.fixture(scope="function")
def document_store(document_db_session) -> DocumentStore:
    return get_document_store(client_session=document_db_session)
