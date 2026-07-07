import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

# Import database instance and configuration class
from database.database import db
from database.models import Config

# Import route blueprints
from routes.home import home_routes
from routes.movies import movie_routes
from routes.discover import discover_routes
from routes.search import search_routes
from routes.person import person_routes
from routes.genres import genre_routes
from routes.auth import auth_routes
from routes.favorite import favorite_routes
from routes.watchlist import watchlist_routes
from routes.review import review_routes 
from routes.history import history_routes       

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)

    # ---------------------------------------------------------
    # LEGACY ROUTES (Prefix omitted because '/api/' is hardcoded)
    # ---------------------------------------------------------
    app.register_blueprint(home_routes)
    app.register_blueprint(movie_routes)
    app.register_blueprint(discover_routes)
    app.register_blueprint(search_routes)
    app.register_blueprint(person_routes)
    app.register_blueprint(genre_routes)
    
    # ---------------------------------------------------------
    # NEW ROUTES (Prefix required to maintain frontend mapping)
    # ---------------------------------------------------------
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(favorite_routes, url_prefix='/api/favorites')
    app.register_blueprint(watchlist_routes, url_prefix='/api/watchlist')
    app.register_blueprint(review_routes, url_prefix='/api/reviews') 
    app.register_blueprint(history_routes, url_prefix='/api/history') 
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)