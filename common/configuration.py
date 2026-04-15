from pydantic_settings import BaseSettings


class Config(BaseSettings):
    document_db_host: str = "localhost"
    document_db_port: int = 27017
    document_db_user: str = "pitch-book"
    document_db_password: str = "dbpasswd"
    document_db_name: str = "pitch-book-document-db"

    @property
    def document_db_uri(self) -> str:
        return f"mongodb://{self.document_db_user}:{self.document_db_password}@{self.document_db_host}:{self.document_db_port}/"
