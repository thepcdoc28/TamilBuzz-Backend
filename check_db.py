from app import app
from database.database import db
from database.models import User
from sqlalchemy import inspect
with app.app_context():
    # 1. Show all tables
    inspector = inspect(db.engine)
    print("--- TABLES IN DATABASE ---")
    for table in inspector.get_table_names():
        print(f"- {table}")
    
    # 2. Show all users
    print("\n--- USERS DATA ---")
    users = User.query.all()
    if not users:
        print("No users found in the database.")
    else:
        for user in users:
            print(f"ID: {user.id} | Username: {user.username} | Email: {user.email}")
