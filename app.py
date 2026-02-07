import gradio as gr
import requests
import os
import pandas as pd
from inference import MoodClassifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load model from HuggingFace
classifier = MoodClassifier('rohanjain2312/distilbert-mood-classifier')

# Get API key from environment (secure)
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

if not GOOGLE_PLACES_API_KEY:
    raise ValueError("GOOGLE_PLACES_API_KEY not found in environment variables. Please set it in HuggingFace Spaces secrets or .env file")

# 30 Major cities worldwide
CITIES = {
    "New York, USA": (40.7580, -73.9855),
    "Los Angeles, USA": (34.0522, -118.2437),
    "San Francisco, USA": (37.7749, -122.4194),
    "Chicago, USA": (41.8781, -87.6298),
    "Boston, USA": (42.3601, -71.0589),
    "Seattle, USA": (47.6062, -122.3321),
    "Miami, USA": (25.7617, -80.1918),
    "Washington DC, USA": (38.9072, -77.0369),
    "London, UK": (51.5074, -0.1278),
    "Paris, France": (48.8566, 2.3522),
    "Tokyo, Japan": (35.6762, 139.6503),
    "Singapore": (1.3521, 103.8198),
    "Hong Kong": (22.3193, 114.1694),
    "Sydney, Australia": (-33.8688, 151.2093),
    "Toronto, Canada": (43.6532, -79.3832),
    "Dubai, UAE": (25.2048, 55.2708),
    "Mumbai, India": (19.0760, 72.8777),
    "Berlin, Germany": (52.5200, 13.4050),
    "Barcelona, Spain": (41.3851, 2.1734),
    "Mexico City, Mexico": (19.4326, -99.1332),
    "Bangalore, India": (12.9716, 77.5946),
    "Mangalore, India": (12.9141, 74.8560),
    "Mysore, India": (12.2958, 76.6394),
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Rome, Italy": (41.9028, 12.4964),
    "Bangkok, Thailand": (13.7563, 100.5018),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "Buenos Aires, Argentina": (-34.6037, -58.3816),
    "São Paulo, Brazil": (-23.5505, -46.6333)
}

def set_city_coords(city):
    """Update coordinates when city is selected"""
    if city in CITIES:
        lat, lng = CITIES[city]
        return lat, lng
    return 40.7580, -73.9855

def get_recommendations(latitude, longitude, mood):
    try:
        # Fetch nearby restaurants
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f'{latitude},{longitude}',
            'radius': 3000,
            'type': 'restaurant',
            'key': GOOGLE_PLACES_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') != 'OK':
            return pd.DataFrame(), f"❌ Error fetching restaurants: {data.get('status')}"
        
        restaurants = [r for r in data.get('results', []) 
                      if r.get('rating', 0) > 3.9 and r.get('user_ratings_total', 0) > 10][:15]
        
        if not restaurants:
            return pd.DataFrame(), "❌ No restaurants found matching criteria in this area."
        
        scored_restaurants = []
        
        for restaurant in restaurants:
            place_id = restaurant['place_id']
            name = restaurant['name']
            location = restaurant.get('geometry', {}).get('location', {})
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            
            # Fetch reviews
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'fields': 'reviews',
                'key': GOOGLE_PLACES_API_KEY
            }
            
            details_response = requests.get(details_url, params=details_params)
            details_data = details_response.json()
            reviews = details_data.get('result', {}).get('reviews', [])
            
            review_texts = [r['text'] for r in reviews if r.get('text') and len(r.get('text', '')) > 20]
            
            if len(review_texts) >= 3:
                mood_score = classifier.aggregate_mood_scores(review_texts, mood)
                
                # Create Google Maps link embedded in address
                address = restaurant.get('vicinity', 'N/A')
                maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={place_id}"
                address_with_link = f'<a href="{maps_link}" target="_blank" style="color: #1a73e8; text-decoration: none;">📍 {address}</a>'
                
                scored_restaurants.append({
                    'Restaurant': name,
                    'Mood Score': f"{mood_score}/10",
                    'Rating': f"⭐ {restaurant.get('rating', 'N/A')}",
                    'Reviews': restaurant.get('user_ratings_total', 0),
                    'Address': address_with_link
                })
        
        # Sort by mood score
        scored_restaurants.sort(key=lambda x: float(x['Mood Score'].split('/')[0]), reverse=True)
        
        if not scored_restaurants:
            return pd.DataFrame(), "❌ Found restaurants but not enough reviews to score."
        
        # Create DataFrame
        df = pd.DataFrame(scored_restaurants[:10])
        
        return df, f"✅ Found {len(scored_restaurants)} restaurants matching your mood!"
        
    except Exception as e:
        return pd.DataFrame(), f"❌ Error: {str(e)}"

# Gradio interface
with gr.Blocks(title="Mood-Based Restaurant Recommender", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🍽️ Mood-Based Restaurant Recommender
    
    Find restaurants that match your mood using AI-powered review analysis with a fine-tuned DistilBERT model.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            city_dropdown = gr.Dropdown(
                choices=sorted(list(CITIES.keys())),
                label="🌍 Choose a City",
                value="New York, USA",
                info="Select from 30 major cities worldwide"
            )
            
            with gr.Row():
                latitude = gr.Number(label="Latitude", value=40.7580, interactive=False)
                longitude = gr.Number(label="Longitude", value=-73.9855, interactive=False)
            
            mood = gr.Radio(
                ["celebration", "date", "quick_bite", "budget"],
                label="🎭 Select Your Mood",
                value="date",
                info="What kind of dining experience are you looking for?"
            )
            
            submit_btn = gr.Button("🔍 Find Restaurants", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            status_msg = gr.Markdown("")
            output_table = gr.Dataframe(
                headers=["Restaurant", "Mood Score", "Rating", "Reviews", "Address"],
                label="Top Recommendations (Click address to view on Google Maps)",
                wrap=True,
                interactive=False,
                datatype=["str", "str", "str", "number", "html"]
            )
    
    # Event handlers
    city_dropdown.change(
        fn=set_city_coords,
        inputs=[city_dropdown],
        outputs=[latitude, longitude]
    )
    
    submit_btn.click(
        fn=get_recommendations,
        inputs=[latitude, longitude, mood],
        outputs=[output_table, status_msg]
    )
    
    gr.Markdown("""
    ---
    
    ## 📊 About This Project
    
    This application uses a **fine-tuned DistilBERT model** to analyze restaurant reviews and match them to your mood. 
    
    ### How It Works:
    1. **Data Collection**: Scraped 1,320+ restaurant reviews from Google Places API across 5 major US cities
    2. **Synthetic Labeling**: Used Groq's Llama 3.1 API to label reviews across 4 mood categories
    3. **Model Training**: Fine-tuned DistilBERT on 227 labeled reviews achieving **0.69 F1 macro** score
    4. **Real-time Analysis**: Fetches nearby restaurants, analyzes reviews, and ranks by mood-fit score (0-10)
    
    ### Technical Stack:
    - **ML Framework**: PyTorch, Transformers (DistilBERT)
    - **Backend**: Python, FastAPI (original), Gradio (deployed)
    - **APIs**: Google Places API, Groq API
    - **Deployment**: HuggingFace Spaces
    
    ### Model Performance:
    | Mood | Precision | Recall | F1-Score |
    |------|-----------|--------|----------|
    | 🎉 Celebration | 1.00 | 0.83 | **0.91** |
    | ⚡ Quick Bite | 0.70 | 0.88 | **0.78** |
    | ❤️ Date | 0.78 | 0.47 | **0.58** |
    | 💰 Budget | 0.40 | 0.57 | **0.47** |
    
    **Overall**: Macro F1 = 0.69 | Micro F1 = 0.75
    
    ---
    
    ### 👨‍💻 Created by Rohan Jain
    
    Master's Student in Applied Machine Learning at University of Maryland (Expected 2026)  
    Former Data Analyst & BI Associate at Goldman Sachs
    
    **Connect with me:**
    
    [<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />](https://www.linkedin.com/in/jaroh23/)
    [<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />](https://github.com/Rohanjain2312)
    [<img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000" />](https://huggingface.co/rohanjain2312)
    
    **Project Links:**
    - 📦 [Model on HuggingFace](https://huggingface.co/rohanjain2312/distilbert-mood-classifier)
    - 💻 [Source Code on GitHub](https://github.com/Rohanjain2312/mood-based-restaurant-recommender)
    - 📓 [Training Notebooks](https://github.com/Rohanjain2312/mood-based-restaurant-recommender/tree/main/notebooks)
    """)

if __name__ == "__main__":
    demo.launch()