from flask import Blueprint, jsonify, request

from services.tmdb_service import discover_movies

discover_routes = Blueprint("discover", __name__)


@discover_routes.route("/api/discover")
def discover():

    page = request.args.get("page", default=1, type=int)

    genre = request.args.get("genre", default=None)

    year = request.args.get("year", default=None)

    rating = request.args.get("rating", default=None)

    sort_by = request.args.get("sort_by", default="popularity.desc")
    media_type = request.args.get("type", default="movie")
    provider = request.args.get("provider", default=None)

    movies = discover_movies(
        page=page,
        genre=genre,
        year=year,
        rating=rating,
        sort_by=sort_by,
        media_type=media_type,
        provider=provider
    )

    return jsonify(movies)