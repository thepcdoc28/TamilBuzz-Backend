from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import db
from database.models import Favorite

favorite_routes = Blueprint('favorite', __name__)

@favorite_routes.route('', methods=['GET'])
@jwt_required()
def get_favorites():
    """Fetch all favorite movie IDs for the authenticated user."""
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.added_at.desc()).all()
    
    return jsonify([
        {"id": fav.id, "movie_id": fav.movie_id, "added_at": fav.added_at} 
        for fav in favorites
    ]), 200


@favorite_routes.route('/<int:movie_id>', methods=['POST'])
@jwt_required()
def add_favorite(movie_id):
    """Add a movie to the user's favorites."""
    user_id = get_jwt_identity()
    
    # Prevent duplicate entries
    existing = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing:
        return jsonify({"message": "Movie is already in favorites"}), 400
        
    new_fav = Favorite(user_id=user_id, movie_id=movie_id)
    
    try:
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({"message": "Added to favorites successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add to favorites due to server error"}), 500


@favorite_routes.route('/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(movie_id):
    """Remove a movie from the user's favorites."""
    user_id = get_jwt_identity()
    
    fav = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not fav:
        return jsonify({"error": "Movie not found in favorites"}), 404
        
    try:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"message": "Removed from favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to remove from favorites"}), 500