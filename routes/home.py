from flask import Blueprint, jsonify

from services.tmdb_service import (

    get_trending_movies,

    get_popular_movies,

    get_top_rated_movies,

    get_upcoming_movies

)

home_routes = Blueprint("home", __name__)


@home_routes.route("/api/home")

def home():

    trending = get_trending_movies()

    popular = get_popular_movies()

    top_rated = get_top_rated_movies()

    upcoming = get_upcoming_movies()

    featured = trending[0] if trending else None

    return jsonify({

        "featured": featured,

        "trending": trending,

        "popular": popular,

        "topRated": top_rated,

        "upcoming": upcoming

    })