import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

CITIES = {
    'NYC': {'lat': 40.7580, 'lng': -73.9855, 'name': 'New York City'},
    'Boston': {'lat': 42.3601, 'lng': -71.0589, 'name': 'Boston'},
    'SF': {'lat': 37.7749, 'lng': -122.4194, 'name': 'San Francisco'},
    'LA': {'lat': 34.0522, 'lng': -118.2437, 'name': 'Los Angeles'},
    'Seattle': {'lat': 47.6062, 'lng': -122.3321, 'name': 'Seattle'}
}

# Types to EXCLUDE (lodging-related)
EXCLUDE_TYPES = {'lodging', 'hotel', 'motel', 'inn', 'hostel', 'resort'}

def fetch_nearby_restaurants(lat, lng, radius=3000):
    """Fetch restaurants using Places API Nearby Search"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    all_results = []
    next_page_token = None
    
    for page in range(3):  # Get up to 60 results (3 pages × 20)
        params = {
            'location': f'{lat},{lng}',
            'radius': radius,
            'type': 'restaurant',
            'key': API_KEY
        }
        
        if next_page_token:
            params['pagetoken'] = next_page_token
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = data.get('results', [])
        all_results.extend(results)
        
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
        
        time.sleep(2)  # Required delay for next_page_token
    
    # Filter: rating > 3.9, reviews > 50, exclude lodging
    filtered = []
    for r in all_results:
        types = set(r.get('types', []))
        if (r.get('rating', 0) > 3.9 and 
            r.get('user_ratings_total', 0) > 50 and
            not types.intersection(EXCLUDE_TYPES)):
            filtered.append(r)
    
    return filtered[:60]  # Top 60 per city

def fetch_place_details(place_id):
    """Fetch detailed info including reviews"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        'place_id': place_id,
        'fields': 'name,rating,user_ratings_total,reviews,formatted_address,types',
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    return response.json().get('result', {})

def collect_reviews_from_cities():
    """Main collection function"""
    all_data = []
    
    for city_code, coords in CITIES.items():
        print(f"\n{'='*50}")
        print(f"Collecting from {coords['name']}...")
        print(f"{'='*50}")
        
        restaurants = fetch_nearby_restaurants(coords['lat'], coords['lng'])
        print(f"Found {len(restaurants)} restaurants matching criteria")
        
        for idx, restaurant in enumerate(restaurants, 1):
            place_id = restaurant['place_id']
            name = restaurant['name']
            
            print(f"  [{idx}/{len(restaurants)}] {name}...", end='')
            
            details = fetch_place_details(place_id)
            reviews = details.get('reviews', [])
            
            # Google API returns max 5 reviews - accept all valid ones
            valid_reviews = [
                r for r in reviews 
                if r.get('text') and len(r.get('text', '')) > 20
            ]
            
            if len(valid_reviews) < 3:  # Need at least 3 reviews
                print(f" SKIP (only {len(valid_reviews)} reviews)")
                continue
            
            print(f" ✓ {len(valid_reviews)} reviews")
            
            restaurant_data = {
                'place_id': place_id,
                'name': name,
                'city': coords['name'],
                'rating': details.get('rating'),
                'user_ratings_total': details.get('user_ratings_total'),
                'address': details.get('formatted_address'),
                'types': details.get('types', []),
                'reviews': [
                    {
                        'text': r['text'],
                        'rating': r['rating'],
                        'time': r.get('time'),
                        'author': r.get('author_name')
                    }
                    for r in valid_reviews
                ]
            }
            
            all_data.append(restaurant_data)
            time.sleep(0.5)
        
        time.sleep(2)
    
    return all_data

def save_data(data):
    """Save collected data"""
    os.makedirs('data/raw', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/raw/restaurant_reviews_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    with open('data/raw/restaurant_reviews_latest.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def print_statistics(data):
    """Print collection statistics"""
    total_restaurants = len(data)
    total_reviews = sum(len(r['reviews']) for r in data)
    reviews_by_city = {}
    
    for r in data:
        city = r['city']
        reviews_by_city[city] = reviews_by_city.get(city, 0) + len(r['reviews'])
    
    print(f"\n{'='*50}")
    print("COLLECTION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Restaurants: {total_restaurants}")
    print(f"Total Reviews: {total_reviews}")
    print(f"\nReviews by City:")
    for city, count in reviews_by_city.items():
        print(f"  {city}: {count} reviews")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    print("Starting restaurant review collection...")
    print(f"Target cities: {', '.join([c['name'] for c in CITIES.values()])}")
    
    data = collect_reviews_from_cities()
    
    if data:
        filename = save_data(data)
        print_statistics(data)
        print(f"✓ Data saved to: {filename}")
    else:
        print("❌ No data collected")