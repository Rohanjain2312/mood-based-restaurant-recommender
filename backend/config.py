import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Model settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/distilbert-mood-classifier')
    
    # API settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    
    # Restaurant filtering criteria
    MIN_RATING = 3.9
    MIN_USER_RATINGS = 10
    MIN_REVIEWS = 3
    
    # Mood categories
    MOODS = ['work', 'date', 'quick_bite', 'budget', 'family', 'late_night', 'celebration']
    
    # Request limits
    MAX_NEARBY_RESTAURANTS = 30
    DEFAULT_RADIUS = 3000
    DEFAULT_MAX_RESULTS = 10

config = Config()