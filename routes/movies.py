from flask import Blueprint, jsonify, request

from services.tmdb_service import *

movie_routes = Blueprint("movies", __name__)


@movie_routes.route("/api/trending")
def trending():
    return jsonify(get_trending_movies())


@movie_routes.route("/api/top-rated")
def top_rated():
    return jsonify(get_top_rated_movies())


@movie_routes.route("/api/upcoming")
def upcoming():
    return jsonify(get_upcoming_movies())


@movie_routes.route("/api/popular")
def popular():
    return jsonify(get_popular_movies())


@movie_routes.route("/api/trending-series")
def trending_series():
    return jsonify(get_trending_series())


@movie_routes.route("/api/top-rated-series")
def top_rated_series():
    return jsonify(get_top_rated_series())


@movie_routes.route("/api/popular-series")
def popular_series():
    return jsonify(get_popular_series())


@movie_routes.route("/api/action")
def action_movies():
    return jsonify(get_action_movies())


@movie_routes.route("/api/comedy")
def comedy_movies():
    return jsonify(get_comedy_movies())


@movie_routes.route("/api/movie/<int:movie_id>")
def movie(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_movie_details(movie_id, media_type))


@movie_routes.route("/api/movie/<int:movie_id>/videos")
def videos(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_movie_videos(movie_id, media_type))


@movie_routes.route("/api/movie/<int:movie_id>/providers")
def providers(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_watch_providers(movie_id, media_type))


@movie_routes.route("/api/movie/<int:movie_id>/cast")
def cast(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_cast(movie_id, media_type))


@movie_routes.route("/api/movie/<int:movie_id>/crew")
def crew(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_crew(movie_id, media_type))


@movie_routes.route("/api/movie/<int:movie_id>/similar")
def similar(movie_id):
    media_type = request.args.get("type", "movie")
    return jsonify(get_similar_movies(movie_id, media_type))


@movie_routes.route("/api/search/<query>")
def search(query):
    return jsonify(search_movies(query))