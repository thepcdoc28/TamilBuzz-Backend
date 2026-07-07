from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database.database import db
from database.models import User
from services.auth_services import hash_password, verify_password

# Initialize the blueprint
auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    """Handle new user registration"""
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields (username, email, password)"}), 400

    # Check for existing email or username
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken"}), 409

    # Hash the password and save to database
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()

        # Generate a login token immediately upon registration
        access_token = create_access_token(identity=str(new_user.id))

        return jsonify({
            "message": "Registration successful",
            "token": access_token,
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed due to a server error."}), 500


@auth_routes.route('/login', methods=['POST'])
def login():
    """Handle user login and token generation"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    # Fetch user from the database
    user = User.query.filter_by(email=email).first()

    # Verify user exists and password matches
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


@auth_routes.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Fetch current user profile. Requires valid JWT."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "joined": user.created_at.strftime('%Y-%m-%d')
        }
    }), 200