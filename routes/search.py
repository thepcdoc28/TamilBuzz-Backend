from flask import Blueprint, jsonify, request

from services.tmdb_service import search_movies, search_person

search_routes = Blueprint("search", __name__)

@search_routes.route("/api/search")
def search():
    query = request.args.get("query", "")
    page = request.args.get("page", default=1, type=int)
    search_type = request.args.get("type", "movie")

    if query.strip() == "":
        return jsonify([])

    if search_type == "actor":
        movies = search_person(query=query, department="Acting", page=page)
    elif search_type == "director":
        movies = search_person(query=query, department="Directing", page=page)
    else:
        movies = search_movies(query=query, page=page)

    return jsonify(movies)