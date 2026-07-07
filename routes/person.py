from flask import Blueprint, jsonify, request
from services.tmdb_service import (
    get_person_details,
    get_person_movies,
    get_person_images,
    get_person_external_ids,
    get_popular_people,
    get_popular_directors
)

person_routes = Blueprint("person", __name__)

@person_routes.route("/api/person/<int:person_id>")
def person_details(person_id):
    return jsonify(get_person_details(person_id))

@person_routes.route("/api/person/<int:person_id>/movies")
def person_movies(person_id):
    return jsonify(get_person_movies(person_id))

@person_routes.route("/api/person/<int:person_id>/images")
def person_images(person_id):
    return jsonify(get_person_images(person_id))

@person_routes.route("/api/person/<int:person_id>/external")
def person_external(person_id):
    return jsonify(get_person_external_ids(person_id))

@person_routes.route("/api/person/popular")
def popular_people():
    # Capture the 'page' parameter from the React frontend, defaulting to 1
    page = request.args.get('page', default=1, type=int)
    
    # Pass the page number to our new dynamic Tamil Actor generator
    return jsonify(get_popular_people(page))

@person_routes.route("/api/person/popular-directors")
def popular_directors_route():
    page = request.args.get('page', default=1, type=int)
    return jsonify(get_popular_directors(page))