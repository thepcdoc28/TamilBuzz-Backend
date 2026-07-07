from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import db
from database.models import Review, User

review_routes = Blueprint('review', __name__)

@review_routes.route('/<int:movie_id>', methods=['GET'])
def get_reviews(movie_id):
    """
    Fetch all user reviews for a specific movie.
    Public access endpoint—no token required.
    """
    # Perform a relational join to pull the username along with the review data
    reviews = db.session.query(Review, User.username).join(
        User, Review.user_id == User.id
    ).filter(
        Review.movie_id == movie_id
    ).order_by(
        Review.created_at.desc()
    ).all()
    
    return jsonify([
        {
            "id": review.id,
            "user_id": review.user_id,
            "username": username,
            "rating": review.rating,
            "review_text": review.review_text,
            "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for review, username in reviews
    ]), 200


@review_routes.route('/<int:movie_id>', methods=['POST'])
@jwt_required()
def add_review(movie_id):
    """
    Submit a new movie review and rating.
    Protected endpoint—requires valid JWT.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    rating = data.get('rating')
    review_text = data.get('review_text', '').strip()

    # Request Validation
    if rating is None:
        return jsonify({"error": "Rating field is required"}), 400

    try:
        rating = float(rating)
        if rating < 1 or rating > 10:
            return jsonify({"error": "Rating must be an integer or float between 1.0 and 10.0"}), 400
    except ValueError:
        return jsonify({"error": "Rating must be a numeric value"}), 400

    # Business Rule: Prevent duplicate reviews by the same user on the same movie
    existing_review = Review.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_review:
        return jsonify({"error": "You have already submitted a review for this movie"}), 400

    new_review = Review(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        review_text=review_text if review_text else None
    )

    try:
        db.session.add(new_review)
        db.session.commit()
        return jsonify({
            "message": "Review published successfully",
            "review_id": new_review.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to store review due to a systemic database error"}), 500


@review_routes.route('/review/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Remove a specific review from the database.
    Protected endpoint—only the author can delete their own review.
    """
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)

    if not review:
        return jsonify({"error": "Review record not found"}), 404

    # Authorization Check
    if review.user_id != user_id:
        return jsonify({"error": "Unauthorized. You can only delete reviews published by your account"}), 403

    try:
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "Review deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to safely purge review from database"}), 500