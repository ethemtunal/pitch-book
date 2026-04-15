from typing import cast

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from pymongo.synchronous.client_session import ClientSession

from adapters.document_stores.document_db.document_store import (
    get_document_store,
    get_document_store_session,
)
from common.types import RatingCreate, SongCreate
from services.song_service import SongService

songs_bp = Blueprint("songs", __name__, url_prefix="/songs")


def _get_service() -> SongService:
    session = cast(ClientSession, request.environ["document_store_session"])
    return SongService(document_store=get_document_store(session))


@songs_bp.before_request
def open_session():
    ctx = get_document_store_session()
    session = ctx.__enter__()
    request.environ["document_store_session"] = session
    request.environ["document_store_ctx"] = ctx


@songs_bp.teardown_request
def close_session(exc):
    ctx = request.environ.get("document_store_ctx")
    if ctx:
        ctx.__exit__(None, None, None)


@songs_bp.post("/")
def add_song():
    try:
        body = SongCreate.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422
    song = _get_service().add_song(body)
    return jsonify(song.model_dump()), 201


@songs_bp.get("/")
def get_songs():
    page_size = request.args.get("page_size", 20, type=int)
    last_id = request.args.get("last_id", None)
    songs = _get_service().get_songs(page_size=page_size, last_id=last_id)
    return jsonify([s.model_dump() for s in songs])


@songs_bp.get("/avg/difficulty")
def avg_difficulty():
    level = request.args.get("level", None, type=int)
    avg = _get_service().get_avg_difficulty(level=level)
    return jsonify({"average": avg})


@songs_bp.get("/search")
def search_songs():
    message = request.args.get("message", "")
    if not message:
        return jsonify({"error": "message parameter is required"}), 400
    songs = _get_service().search_songs(message=message)
    return jsonify([s.model_dump() for s in songs])


@songs_bp.post("/rating")
def add_rating():
    try:
        body = RatingCreate.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422
    _get_service().add_rating(song_id=body.song_id, rating=body.rating)
    return jsonify({"status": "ok"}), 201


@songs_bp.get("/rating/<song_id>")
def get_rating_stats(song_id: str):
    stats = _get_service().get_rating_stats(song_id=song_id)
    return jsonify(stats.model_dump())
