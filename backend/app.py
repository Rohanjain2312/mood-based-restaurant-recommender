from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional
import requests
from dotenv import load_dotenv
from inference import MoodClassifier

load_dotenv()

app = FastAPI(title="Mood-Based Restaurant Recommender API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

# Global classifier instance
classifier = None

@app.on_event("startup")
async def startup_event():
    """Load model at startup"""
    global classifier
    try:
        # Load from HuggingFace instead of local path
        model_path = 'rohanjain2312/distilbert-mood-classifier'
        print(f"Attempting to load model from: {model_path}")
        classifier = MoodClassifier(model_path)
        print(f"Model loaded successfully from HuggingFace: {model_path}")
    except Exception as e:
        import traceback
        print(f"Full error traceback:")
        traceback.print_exc()
        print(f"Warning: Could not load model: {e}. Using placeholder scoring.")
class RecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    mood: str
    radius: int = 3000
    max_results: int = 10

class Restaurant(BaseModel):
    place_id: str
    name: str
    address: str
    rating: float
    user_ratings_total: int
    distance: Optional[float] = None
    mood_score: float
    is_open: Optional[bool] = None
    price_level: Optional[int] = None
    types: List[str]

class RecommendationResponse(BaseModel):
    mood: str
    restaurants: List[Restaurant]
    total_found: int

# Health check endpoint
@app.get("/")
def root():
    return {
        "message": "Mood-Based Restaurant Recommender API",
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": classifier is not None
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": classifier is not None
    }

# Main recommendation endpoint
@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get restaurant recommendations based on user location and mood
    
    Args:
        request: RecommendationRequest with lat, lng, mood, radius, max_results
    
    Returns:
        RecommendationResponse with ranked restaurants
    """
    
    # Validate mood - updated to 4 moods
    valid_moods = ['celebration', 'date', 'quick_bite', 'budget']
    if request.mood not in valid_moods:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
        )
    
    # Fetch nearby restaurants
    try:
        restaurants = fetch_nearby_restaurants(
            request.latitude, 
            request.longitude, 
            request.radius
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")
    
    if not restaurants:
        return RecommendationResponse(
            mood=request.mood,
            restaurants=[],
            total_found=0
        )
    
    # Score and rank restaurants based on mood
    try:
        scored_restaurants = score_restaurants_by_mood(restaurants, request.mood)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring restaurants: {str(e)}")
    
    # Return top results
    top_restaurants = scored_restaurants[:request.max_results]
    
    return RecommendationResponse(
        mood=request.mood,
        restaurants=top_restaurants,
        total_found=len(scored_restaurants)
    )

def fetch_nearby_restaurants(lat: float, lng: float, radius: int) -> List[dict]:
    """
    Fetch nearby restaurants from Google Places API
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,
        'type': 'restaurant',
        'key': GOOGLE_PLACES_API_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Places API error: {response.status_code}")
    
    data = response.json()
    results = data.get('results', [])
    
    # Filter by criteria: rating > 3.9, reviews > 10
    filtered = [
        r for r in results 
        if r.get('rating', 0) > 3.9 and r.get('user_ratings_total', 0) > 10
    ]
    
    return filtered[:30]  # Limit to 30 for processing

def fetch_restaurant_reviews(place_id: str) -> List[str]:
    """
    Fetch reviews for a specific restaurant
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        'place_id': place_id,
        'fields': 'reviews',
        'key': GOOGLE_PLACES_API_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    result = data.get('result', {})
    reviews = result.get('reviews', [])
    
    # Extract review text
    review_texts = [
        r['text'] for r in reviews 
        if r.get('text') and len(r.get('text', '')) > 20
    ]
    
    return review_texts

def score_restaurants_by_mood(restaurants: List[dict], mood: str) -> List[Restaurant]:
    """
    Score and rank restaurants based on mood classification using trained model
    """
    scored_restaurants = []
    
    for restaurant in restaurants:
        place_id = restaurant['place_id']
        
        # Fetch reviews
        reviews = fetch_restaurant_reviews(place_id)
        
        if len(reviews) < 3:
            continue
        
        # Use trained model if available, otherwise fall back to placeholder
        if classifier:
            try:
                mood_score = classifier.aggregate_mood_scores(reviews, mood)
            except Exception as e:
                print(f"Model inference error for {restaurant['name']}: {e}")
                mood_score = calculate_mood_score_placeholder(reviews, mood)
        else:
            mood_score = calculate_mood_score_placeholder(reviews, mood)
        
        # Create Restaurant object
        scored_restaurant = Restaurant(
            place_id=place_id,
            name=restaurant['name'],
            address=restaurant.get('vicinity', ''),
            rating=restaurant.get('rating', 0.0),
            user_ratings_total=restaurant.get('user_ratings_total', 0),
            mood_score=mood_score,
            is_open=restaurant.get('opening_hours', {}).get('open_now'),
            price_level=restaurant.get('price_level'),
            types=restaurant.get('types', [])
        )
        
        scored_restaurants.append(scored_restaurant)
    
    # Sort by mood score descending
    scored_restaurants.sort(key=lambda x: x.mood_score, reverse=True)
    
    return scored_restaurants

def calculate_mood_score_placeholder(reviews: List[str], mood: str) -> float:
    """
    Placeholder function for mood scoring when model is not available
    Simple keyword-based scoring for fallback
    """
    # Updated to 4 moods only
    mood_keywords = {
        'celebration': ['special', 'birthday', 'celebration', 'fancy', 'upscale', 'anniversary', 'occasion'],
        'date': ['romantic', 'intimate', 'ambiance', 'cozy', 'date', 'candles', 'dim'],
        'quick_bite': ['fast', 'quick', 'casual', 'grab', 'counter', 'takeout', 'to-go'],
        'budget': ['cheap', 'affordable', 'value', 'inexpensive', 'budget', 'reasonable', 'deal']
    }
    
    keywords = mood_keywords.get(mood, [])
    score = 0.0
    
    for review in reviews:
        review_lower = review.lower()
        for keyword in keywords:
            if keyword in review_lower:
                score += 1
    
    # Normalize to 0-10 scale
    max_possible_score = len(reviews) * len(keywords)
    if max_possible_score > 0:
        normalized_score = (score / max_possible_score) * 10
    else:
        normalized_score = 5.0  # Default
    
    return round(normalized_score, 2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)