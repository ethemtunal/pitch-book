from pymongo.client_session import ClientSession

from common.configuration import Config


class MongoDBClientCommon:
    def __init__(
        self, client_session: ClientSession, document_db_name: str | None = None
    ):
        self.client_session = client_session
        self.db = client_session.client[document_db_name or Config().document_db_name]
