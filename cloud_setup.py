from app import app
from database.database import db
import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

with app.app_context():
    db.create_all()
    print("cloud database tables created successfully!")