import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_recommendations():
    """Test recommendations endpoint"""
    payload = {
        "latitude": 40.7580,
        "longitude": -73.9855,
        "mood": "date",
        "radius": 3000,
        "max_results": 5
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    print(f"Recommendations: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Mood: {data['mood']}")
        print(f"Total found: {data['total_found']}")
        print(f"\nTop {len(data['restaurants'])} restaurants:")
        for i, rest in enumerate(data['restaurants'], 1):
            print(f"\n{i}. {rest['name']}")
            print(f"   Rating: {rest['rating']} ({rest['user_ratings_total']} reviews)")
            print(f"   Mood Score: {rest['mood_score']}/10")
            print(f"   Address: {rest['address']}")
    else:
        print(json.dumps(response.json(), indent=2))
    
    print("-" * 50)

if __name__ == "__main__":
    print("Testing Mood-Based Restaurant Recommender API\n")
    test_health_check()
    test_recommendations()