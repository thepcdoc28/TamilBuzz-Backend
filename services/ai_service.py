import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from services.tmdb_service import search_movies

def get_ai_movie_recommendations(user_prompt):
    """
    Sends the user's prompt to Gemini AI to get movie recommendations.
    Returns a list of movie titles.
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key is not configured"}
        
    try:
        # Create a Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        system_instructions = """
        You are a Tamil movie expert and matchmaker. 
        The user will give you a prompt describing the kind of movie they want to watch. 
        You must recommend exactly 5 Tamil movies that best match their description.
        Only recommend movies that exist and are originally in the Tamil language.
        
        Respond ONLY with a valid JSON array of strings containing the movie titles.
        Example output:
        ["Vikram", "Kaithi", "Maanagaram", "Theeran Adhigaaram Ondru", "Vada Chennai"]
        
        Do not include markdown tags (like ```json), do not include any other text, just the raw JSON array.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_instructions + "\n\nUser Request: " + user_prompt
        )
        
        text = response.text.strip()
        
        # Clean up any potential markdown formatting the AI might still add
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        try:
            movie_titles = json.loads(text)
            if not isinstance(movie_titles, list):
                raise ValueError("Expected a JSON array")
                
            # Fetch TMDB data for these titles
            results = []
            for title in movie_titles:
                # Use our existing TMDB search logic
                search_data = search_movies(title, page=1)
                
                # The search_movies function already filters for Tamil (ta) and requires a poster
                if search_data.get("results"):
                    # We just take the first result which is usually the most relevant match for the title
                    results.append(search_data["results"][0])
            
            return {"movies": results}
            
        except json.JSONDecodeError:
            print("Failed to parse Gemini output as JSON:", text)
            return {"error": "AI provided an invalid response format"}
            
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return {"error": "Failed to generate recommendations from AI"}
