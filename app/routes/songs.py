from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.song import Song

songs_bp = Blueprint("songs", __name__)

@songs_bp.route("/songs", methods=["GET"])
def list_songs():
    songs = Song.select()
    return jsonify([model_to_dict(s) for s in songs])

@songs_bp.route("/songs", methods=["POST"])
def create_song():
    data = request.get_json()

    if not data:
        return jsonify(error="No data provided"), 400

    required = ["title", "artist", "genre", "duration"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify(error=f"Missing fields: {missing}"), 400

    song = Song.create(
        title=data["title"],
        artist=data["artist"],
        genre=data["genre"],
        duration=data["duration"]
    )
    return jsonify(model_to_dict(song)), 201

@songs_bp.route("/songs/<int:song_id>", methods=["GET"])
def get_song(song_id):
    try:
        song = Song.get_by_id(song_id)
        return jsonify(model_to_dict(song))
    except Song.DoesNotExist:
        return jsonify(error="Song not found"), 404