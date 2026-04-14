from http import HTTPStatus


class PitchBookException(Exception):
    """Base class for all PitchBook exceptions."""

    message: str
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class BadRequest(PitchBookException):
    status_code = HTTPStatus.BAD_REQUEST


class NotFound(PitchBookException):
    status_code = HTTPStatus.NOT_FOUND
