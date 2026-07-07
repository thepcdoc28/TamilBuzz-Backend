from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import db
from database.models import Watchlist

watchlist_routes = Blueprint('watchlist', __name__)

@watchlist_routes.route('', methods=['GET'])
@jwt_required()
def get_watchlist():
    """Fetch all watchlist movie IDs for the authenticated user."""
    user_id = get_jwt_identity()
    watchlist_items = Watchlist.query.filter_by(user_id=user_id).order_by(Watchlist.added_at.desc()).all()
    
    return jsonify([
        {"id": item.id, "movie_id": item.movie_id, "added_at": item.added_at} 
        for item in watchlist_items
    ]), 200


@watchlist_routes.route('/<int:movie_id>', methods=['POST'])
@jwt_required()
def add_to_watchlist(movie_id):
    """Add a movie to the user's watchlist."""
    user_id = get_jwt_identity()
    
    # Prevent duplicate entries
    existing = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing:
        return jsonify({"message": "Movie is already in watchlist"}), 400
        
    new_item = Watchlist(user_id=user_id, movie_id=movie_id)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Added to watchlist successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add to watchlist due to server error"}), 500


@watchlist_routes.route('/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(movie_id):
    """Remove a movie from the user's watchlist."""
    user_id = get_jwt_identity()
    
    item = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not item:
        return jsonify({"error": "Movie not found in watchlist"}), 404
        
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Removed from watchlist successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to remove from watchlist"}), 500