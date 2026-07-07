import os
import pymysql
from dotenv import load_dotenv
from app import app
from database.database import db

load_dotenv()

def setup():
    print("⏳ Connecting to MySQL Server...")
    try:
        # 1. Connect to MySQL without specifying a database to force-create it
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS tamilbuzz")
        conn.close()
        print("✅ Database 'tamilbuzz' verified/created.")
        
    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL Connection Failed: {e}")
        print("ACTION REQUIRED: Your DB_PASSWORD inside backend/.env is incorrect, or your MySQL server is not running.")
        return

    # 2. Bind to the newly created database and build the tables
    print("⏳ Building tables...")
    try:
        with app.app_context():
            db.create_all()
            print("✅ All MySQL tables successfully created!")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")

if __name__ == '__main__':
    setup()