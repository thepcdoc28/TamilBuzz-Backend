import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"


class Config:

    SQLALCHEMY_DATABASE_URI = (

        f"mysql+pymysql://"

        f"{os.getenv('DB_USER')}:"

        f"{os.getenv('DB_PASSWORD')}@"

        f"{os.getenv('DB_HOST')}:"

        f"{os.getenv('DB_PORT')}/"

        f"{os.getenv('DB_NAME')}"

    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")