from app import app
from database.database import db
from database.models import User, Favorite, Watchlist, Review, RecentlyViewed

def initialize_database():
    with app.app_context():
        # This scans models.py and builds the exact tables in MySQL
        db.create_all()
        print("✅ MySQL Database tables successfully created!")

if __name__ == '__main__':
    initialize_database()

