from flask import Flask, jsonify

from adapters.document_stores.document_db.document_store import init_db
from api.routes import songs_bp
from common.exceptions import PitchBookException


def create_app() -> Flask:
    app = Flask(__name__)

    init_db()
    app.register_blueprint(songs_bp)

    @app.errorhandler(PitchBookException)
    def handle_pitch_book_exception(e: PitchBookException):
        return jsonify({"error": e.message}), e.status_code

    return app
