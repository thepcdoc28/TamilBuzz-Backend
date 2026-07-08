import requests
from config import BASE_URL, TMDB_API_KEY

# Use a persistent session to reuse connections and avoid rate-limit blocking
session = requests.Session()

# ------------------------------------
# Common Request Function
# ------------------------------------
def fetch(endpoint, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = session.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Fetch Error: {e}")
        
    return {}

# ------------------------------------
# DATA PURIFIER: Kills "No Poster" & Adult Cards
# ------------------------------------
import re

def clean_media_data(movies_list):
    """
    Filters out any media from TMDb that do not have a poster image,
    strictly blocks any content flagged as adult/18+, and aggressively 
    filters unflagged adult content using a keyword blacklist.
    """
    blocked_keywords = [
        'erotic', 'erotica', 'lust', 'sex', 'porn', 'sensual', 
        'seduction', '18\+', 'b-grade', 'desire', 'intimacy', 'prostitute', 
        'call girl', 'gigolo', 'nymphomaniac', 'anaagarigam'
    ]
    
    # Create a regex pattern to match any of the words as whole words
    pattern = re.compile(rf'\b(?:{"|".join(blocked_keywords)})\b', re.IGNORECASE)
    
    cleaned = []
    for media in movies_list:
        # 1. Official TMDb Adult Flag & Poster Check
        if not media.get("poster_path") or media.get("adult"):
            continue
            
        # 2. Heuristic Keyword Blocklist
        title = media.get('title', media.get('name', ''))
        original_title = media.get('original_title', media.get('original_name', ''))
        text_to_check = f"{title} {original_title} {media.get('overview', '')}"
        
        if not pattern.search(text_to_check):
            if 'media_type' not in media:
                media['media_type'] = 'tv' if 'first_air_date' in media else 'movie'
            cleaned.append(media)
            
    return cleaned

# ------------------------------------
# Base Movie Endpoints
# ------------------------------------
def get_trending_movies():
    p1 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "include_adult": "false", "page": 1})
    p2 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "include_adult": "false", "page": 2})
    return clean_media_data(p1.get("results", []) + p2.get("results", []))

def get_top_rated_movies():
    p1 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "vote_average.desc", "vote_count.gte": 25, "include_adult": "false", "page": 1})
    p2 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "vote_average.desc", "vote_count.gte": 25, "include_adult": "false", "page": 2})
    return clean_media_data(p1.get("results", []) + p2.get("results", []))

def get_upcoming_movies():
    p1 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "primary_release_date.desc", "include_adult": "false", "page": 1})
    p2 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "primary_release_date.desc", "include_adult": "false", "page": 2})
    return clean_media_data(p1.get("results", []) + p2.get("results", []))

def get_popular_movies():
    p1 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "vote_count.desc", "include_adult": "false", "page": 1})
    p2 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "vote_count.desc", "include_adult": "false", "page": 2})
    return clean_media_data(p1.get("results", []) + p2.get("results", []))

# ------------------------------------
# Movie Details
# ------------------------------------
def get_movie_details(movie_id, media_type="movie"):
    return fetch(f"/{media_type}/{movie_id}")

def get_movie_videos(movie_id, media_type="movie"):
    return fetch(f"/{media_type}/{movie_id}/videos", {"include_video_language": "ta,en,te,hi,ml,kn,null"})

def get_watch_providers(movie_id, media_type="movie"):
    return fetch(f"/{media_type}/{movie_id}/watch/providers")

def get_cast(movie_id, media_type="movie"):
    data = fetch(f"/{media_type}/{movie_id}/credits")
    return data.get("cast", [])

def get_crew(movie_id, media_type="movie"):
    data = fetch(f"/{media_type}/{movie_id}/credits")
    return data.get("crew", [])

# ------------------------------------
# Similar Movies
# ------------------------------------
def get_similar_movies(movie_id, media_type="movie"):
    data = fetch(f"/{media_type}/{movie_id}/similar")
    tamil_movies = [m for m in data.get("results", []) if m.get("original_language") == "ta"]
    
    # Fallback 1: Try recommendations if /similar yielded no Tamil results
    if not tamil_movies:
        rec_data = fetch(f"/{media_type}/{movie_id}/recommendations")
        tamil_movies = [m for m in rec_data.get("results", []) if m.get("original_language") == "ta"]
        
    # Fallback 2: If still empty, discover popular Tamil movies in the same genre
    if not tamil_movies:
        details = fetch(f"/{media_type}/{movie_id}")
        if details.get("genres"):
            genre_ids = ",".join([str(g["id"]) for g in details["genres"][:2]])
            disc_data = fetch("/discover/movie", {
                "with_original_language": "ta", 
                "with_genres": genre_ids, 
                "sort_by": "popularity.desc"
            })
            tamil_movies = disc_data.get("results", [])

    # Filter out the current movie itself if it accidentally got included
    tamil_movies = [m for m in tamil_movies if str(m.get("id")) != str(movie_id)]
    
    return clean_media_data(tamil_movies)

# ------------------------------------
# Discover
# ------------------------------------
def discover_movies(page=1, genre=None, year=None, rating=None, sort_by="popularity.desc", media_type="movie"):
    # If "all", interleave both movie and tv endpoints
    if media_type == "all":
        movie_params = { "page": page, "sort_by": sort_by, "with_original_language": "ta", "include_adult": "false" }
        if genre: movie_params["with_genres"] = genre
        if year: movie_params["primary_release_year"] = year
        if rating: movie_params["vote_average.gte"] = rating
        
        tv_params = { 
            "page": page, 
            "sort_by": sort_by, 
            "with_original_language": "ta", 
            "include_adult": "false",
            "watch_region": "IN",
            "with_watch_providers": "8|119|122|220|237|100|319" # Netflix, Amazon, Hotstar, ZEE5, SonyLIV, Apple, JioCinema
        }
        if genre: tv_params["with_genres"] = genre
        if year: tv_params["first_air_date_year"] = year
        if rating: tv_params["vote_average.gte"] = rating
        
        movie_data = fetch("/discover/movie", movie_params)
        tv_data = fetch("/discover/tv", tv_params)
        
        combined_results = movie_data.get("results", []) + tv_data.get("results", [])
        # Sort by popularity or vote_average depending on sort_by (simplistic fallback to popularity)
        sort_key = "vote_average" if "vote_average" in sort_by else "popularity"
        combined_results.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
        
        return {
            "page": page,
            "results": clean_media_data(combined_results)[:20],
            "total_pages": max(movie_data.get("total_pages", 1), tv_data.get("total_pages", 1))
        }

    # Otherwise fetch specific type
    endpoint = f"/discover/{media_type}"
    params = {
        "page": page,
        "sort_by": sort_by,
        "with_original_language": "ta",   
        "include_adult": "false"
    }
    
    if media_type == "tv":
        params["watch_region"] = "IN"
        params["with_watch_providers"] = "8|119|122|220|237|100|319" # Block daily soaps, only OTT Web Series
    if genre: params["with_genres"] = genre
    if year:
        if media_type == "tv":
            params["first_air_date_year"] = year
        else:
            params["primary_release_year"] = year
    if rating: params["vote_average.gte"] = rating
    
    data = fetch(endpoint, params)
    data["results"] = clean_media_data(data.get("results", []))
    return data

# ------------------------------------
# Search
# ------------------------------------
def search_movies(query, page=1):
    params = {
        "query": query,
        "page": page,
        "include_adult": False,
        "language": "en-US"
    }
    data = fetch("/search/movie", params)
    
    # Filter for Tamil AND ensure they have a poster
    filtered_results = [
        movie for movie in data.get("results", []) 
        if movie.get("original_language") == "ta" and movie.get("poster_path")
    ]
    
    return {
        "page": data.get("page", page),
        "results": filtered_results,
        "total_pages": data.get("total_pages", 1)
    }

def search_person(query, department=None, page=1):
    params = {
        "query": query,
        "page": page,
        "include_adult": False,
        "language": "en-US"
    }
    data = fetch("/search/person", params)
    
    results = data.get("results", [])
    
    # Optionally filter results by department (e.g. 'Acting' or 'Directing')
    if department:
        results = [person for person in results if person.get("known_for_department") == department]
        
    return {
        "page": data.get("page", page),
        "results": results,
        "total_pages": data.get("total_pages", 1)
    }

# ------------------------------------
# Person Details
# ------------------------------------
def get_person_details(person_id):
    return fetch(f"/person/{person_id}")

def get_person_images(person_id):
    return fetch(f"/person/{person_id}/images")

def get_person_external_ids(person_id):
    return fetch(f"/person/{person_id}/external_ids")

# ------------------------------------
# Actor's Movies
# ------------------------------------
def get_person_movies(person_id):
    data = fetch(f"/person/{person_id}/combined_credits")
    
    filtered_cast = [m for m in data.get("cast", []) if m.get("original_language") == "ta"]
    filtered_crew = [m for m in data.get("crew", []) if m.get("original_language") == "ta"]
    
    # Apply poster filter to actor's filmography
    data["cast"] = clean_media_data(filtered_cast)
    data["crew"] = clean_media_data(filtered_crew)
    return data

# ------------------------------------
# Popular People (RATE-LIMIT SAFE)
# ------------------------------------
def get_popular_people(page=1):
    movies_data = fetch(
        "/discover/movie",
        {
            "with_original_language": "ta",
            "sort_by": "popularity.desc",
            "page": page
        }
    )
    
    tamil_people = []
    seen_ids = set()
    
    # REDUCED to 3 movies to bypass TMDb's "429 Too Many Requests" block
    for movie in movies_data.get("results", [])[:3]:
        credits = fetch(f"/movie/{movie['id']}/credits")
        
        # INCREASED to 12 cast members to ensure the grid stays full
        for person in credits.get("cast", [])[:12]:
            if person["id"] not in seen_ids and person.get("profile_path"):
                tamil_people.append(person)
                seen_ids.add(person["id"])
                
        for person in credits.get("crew", []):
            if person.get("job") == "Director" and person["id"] not in seen_ids and person.get("profile_path"):
                tamil_people.append(person)
                seen_ids.add(person["id"])
                
    return {
        "page": page,
        "results": tamil_people,
        "total_pages": movies_data.get("total_pages", 1)
    }

# ------------------------------------
# Popular Directors
# ------------------------------------
import concurrent.futures

def get_popular_directors(page=1):
    movies_data_1 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "page": (page * 2) - 1})
    movies_data_2 = fetch("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "page": page * 2})
    
    combined_movies = movies_data_1.get("results", []) + movies_data_2.get("results", [])
    
    tamil_directors = []
    seen_ids = set()
    
    def fetch_movie_director(movie):
        credits = fetch(f"/movie/{movie['id']}/credits")
        directors = []
        for person in credits.get("crew", []):
            if person.get("job") == "Director" and person.get("profile_path"):
                directors.append(person)
        return directors

    # Fetch movie credits concurrently (5 workers to respect rate limits while remaining extremely fast)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        all_directors = executor.map(fetch_movie_director, combined_movies)
        
    for movie_directors in all_directors:
        for person in movie_directors:
            if person["id"] not in seen_ids:
                tamil_directors.append(person)
                seen_ids.add(person["id"])
                
    return {
        "page": page,
        "results": tamil_directors,
        "total_pages": movies_data_1.get("total_pages", 1) // 2
    }

# ------------------------------------
# Genre / Language Utils
# ------------------------------------
def get_genres():
    return fetch("/genre/movie/list", {"language": "en-US"})

def get_languages():
    return fetch("/configuration/languages")

def get_movies_by_genre(genre_id, page=1):
    data = fetch(
        "/discover/movie",
        {"page": page, "with_genres": genre_id, "with_original_language": "ta", "sort_by": "popularity.desc"}
    )
    data["results"] = clean_movie_data(data.get("results", []))
    return data