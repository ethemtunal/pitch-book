from flask import Flask, jsonify

from api.routes import songs_bp
from common.exceptions import PitchBookException


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(songs_bp)

    @app.errorhandler(PitchBookException)
    def handle_pitch_book_exception(e: PitchBookException):
        return jsonify({"error": e.message}), e.status_code

    return app
