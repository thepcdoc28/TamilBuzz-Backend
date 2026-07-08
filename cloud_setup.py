from app import app
from database.database import db

with app.app_context():
    db.create_all()
    print("cloud database tables created successfully!")