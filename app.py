import gradio as gr
import requests
import os
from inference import MoodClassifier

# Load model from HuggingFace
classifier = MoodClassifier('rohanjain2312/distilbert-mood-classifier')

# Get API key from environment
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', 'AIzaSyDtUbq6CIdbaTtKjEW9RXeC2tyWAFYIGfI')

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
            return f"Error fetching restaurants: {data.get('status')}"
        
        restaurants = [r for r in data.get('results', []) 
                      if r.get('rating', 0) > 3.9 and r.get('user_ratings_total', 0) > 10][:15]
        
        if not restaurants:
            return "No restaurants found matching criteria in this area."
        
        scored_restaurants = []
        
        for restaurant in restaurants:
            place_id = restaurant['place_id']
            name = restaurant['name']
            
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
                
                scored_restaurants.append({
                    'name': name,
                    'mood_score': mood_score,
                    'rating': restaurant.get('rating', 'N/A'),
                    'address': restaurant.get('vicinity', 'N/A'),
                    'reviews_count': restaurant.get('user_ratings_total', 0)
                })
        
        # Sort by mood score
        scored_restaurants.sort(key=lambda x: x['mood_score'], reverse=True)
        
        if not scored_restaurants:
            return "Found restaurants but not enough reviews to score."
        
        # Format results
        results = []
        for idx, r in enumerate(scored_restaurants[:10], 1):
            results.append(
                f"**{idx}. {r['name']}**\n"
                f"   🎯 Mood Score: {r['mood_score']}/10\n"
                f"   ⭐ Rating: {r['rating']} ({r['reviews_count']} reviews)\n"
                f"   📍 {r['address']}\n"
            )
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio interface
with gr.Blocks(title="Mood-Based Restaurant Recommender") as demo:
    gr.Markdown("""
    # 🍽️ Mood-Based Restaurant Recommender
    
    Find restaurants that match your mood using AI-powered review analysis.
    """)
    
    with gr.Row():
        with gr.Column():
            latitude = gr.Number(label="Latitude", value=40.7580)
            longitude = gr.Number(label="Longitude", value=-73.9855)
            mood = gr.Radio(
                ["celebration", "date", "quick_bite", "budget"],
                label="Select Your Mood",
                value="date"
            )
            submit_btn = gr.Button("Find Restaurants", variant="primary")
        
        with gr.Column():
            output = gr.Markdown(label="Recommendations")
    
    submit_btn.click(
        fn=get_recommendations,
        inputs=[latitude, longitude, mood],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()