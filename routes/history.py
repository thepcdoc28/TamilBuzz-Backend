from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import db
from database.models import RecentlyViewed
import datetime

from services.tmdb_service import get_movie_details

history_routes = Blueprint('history', __name__)

@history_routes.route('', methods=['GET'])
@jwt_required()
def get_history():
    """
    Fetch the 15 most recently viewed movies for the authenticated user.
    """
    user_id = get_jwt_identity()
    
    history_records = RecentlyViewed.query.filter_by(user_id=user_id)\
        .order_by(RecentlyViewed.viewed_at.desc())\
        .limit(15).all()
        
    results = []
    for item in history_records:
        details = get_movie_details(item.movie_id)
        if details and 'id' in details:
            # Add viewed_at to the movie details object so the frontend knows when they watched it
            details['viewed_at'] = item.viewed_at.strftime('%Y-%m-%d %H:%M:%S')
            details['history_id'] = item.id
            results.append(details)
            
    return jsonify(results), 200


@history_routes.route('/<int:movie_id>', methods=['POST'])
@jwt_required()
def update_history(movie_id):
    """
    Log a movie as viewed. If it already exists in the user's history,
    bump the timestamp to the current time.
    """
    user_id = get_jwt_identity()
    
    existing_record = RecentlyViewed.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    
    if existing_record:
        existing_record.viewed_at = datetime.datetime.utcnow()
    else:
        new_record = RecentlyViewed(user_id=user_id, movie_id=movie_id)
        db.session.add(new_record)
        
    try:
        db.session.commit()
        return jsonify({"message": "Viewing history successfully updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to sync history with database"}), 500
