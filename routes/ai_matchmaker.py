from flask import Blueprint, jsonify, request
from services.ai_service import get_ai_movie_recommendations

ai_routes = Blueprint("ai_matchmaker", __name__)

@ai_routes.route("/api/matchmaker", methods=["POST"])
def matchmaker():
    data = request.get_json()
    
    if not data or not data.get("prompt"):
        return jsonify({"error": "No prompt provided"}), 400
        
    prompt = data.get("prompt")
    
    # Generate recommendations using Gemini
    result = get_ai_movie_recommendations(prompt)
    
    if "error" in result:
        return jsonify({"error": result["error"]}), 500
        
    return jsonify(result)
