from flask import Blueprint, jsonify

from services.tmdb_service import (
    get_genres,
    get_languages,
    get_movies_by_genre
)

genre_routes = Blueprint("genres", __name__)


@genre_routes.route("/api/genres")
def genres():

    return jsonify(get_genres())


@genre_routes.route("/api/languages")
def languages():

    return jsonify(get_languages())


@genre_routes.route("/api/genre/<int:genre_id>")
def genre_movies(genre_id):

    return jsonify(

        get_movies_by_genre(genre_id)

    )