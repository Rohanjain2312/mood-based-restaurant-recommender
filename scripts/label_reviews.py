import json
import os
from groq import Groq
from dotenv import load_dotenv
import time
from tqdm import tqdm

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Define mood categories with clear criteria
MOOD_DEFINITIONS = """
Mood Categories:
1. work: Quiet atmosphere, WiFi mentioned, good for laptops/studying, coffee shop vibes, professional setting
2. date: Romantic ambiance, intimate setting, dim lighting, good for couples, special occasions
3. quick_bite: Fast service, casual, grab-and-go, counter service, quick meal mentions
4. budget: Affordable, good value, cheap, inexpensive, reasonable prices mentioned
5. family: Kid-friendly, family atmosphere, high chairs, children mentioned positively
6. late_night: Open late, late-night food, after-hours, nightlife mentions
7. celebration: Special occasions, birthday-friendly, upscale, fancy, celebratory atmosphere
"""

def create_labeling_prompt(review_text):
    """Create prompt for Groq to label a single review"""
    prompt = f"""{MOOD_DEFINITIONS}

Review: "{review_text}"

Analyze this restaurant review and classify it into one or more mood categories.
Return ONLY a JSON object with this exact format:
{{"moods": ["mood1", "mood2"], "confidence": 0.85}}

Rules:
- moods: array of applicable mood strings from the 7 categories above
- confidence: float between 0 and 1 indicating overall classification confidence
- A review can have multiple moods (multi-label)
- Only include moods that clearly apply based on the review content
- If no clear mood applies, return empty array with low confidence

Response:"""
    
    return prompt

def label_single_review(review_text, max_retries=3):
    """Label a single review using Groq API"""
    prompt = create_labeling_prompt(review_text)
    
    for attempt in range(max_retries):
        try:
            # Call Groq API
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=100,
            )
            
            # Parse response
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Extract JSON (handle potential markdown formatting)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate format
            if 'moods' in result and 'confidence' in result:
                return result
            else:
                print(f"Invalid format in response: {result}")
                continue
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                return {"moods": [], "confidence": 0.0}
            time.sleep(1)
            
        except Exception as e:
            print(f"API error (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                return {"moods": [], "confidence": 0.0}
            time.sleep(2)
    
    return {"moods": [], "confidence": 0.0}

def label_all_reviews(input_file, output_file, min_confidence=0.5):
    """Label all reviews from collected data"""
    # Load raw data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Flatten reviews with metadata
    all_reviews = []
    for restaurant in data:
        for review in restaurant['reviews']:
            all_reviews.append({
                'restaurant_name': restaurant['name'],
                'city': restaurant['city'],
                'place_id': restaurant['place_id'],
                'review_text': review['text'],
                'review_rating': review['rating'],
                'review_author': review['author'],
            })
    
    print(f"Total reviews to label: {len(all_reviews)}")
    
    # Label each review
    labeled_reviews = []
    skipped_count = 0
    
    for review in tqdm(all_reviews, desc="Labeling reviews"):
        label_result = label_single_review(review['review_text'])
        
        # Skip low confidence labels
        if label_result['confidence'] < min_confidence:
            skipped_count += 1
            continue
        
        # Add labels to review
        review['moods'] = label_result['moods']
        review['mood_confidence'] = label_result['confidence']
        
        labeled_reviews.append(review)
        
        # Rate limiting (Groq free tier)
        time.sleep(0.1)
    
    print(f"\nLabeling complete:")
    print(f"  Total labeled: {len(labeled_reviews)}")
    print(f"  Skipped (low confidence): {skipped_count}")
    
    # Save labeled data
    os.makedirs('data/labeled', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(labeled_reviews, f, indent=2, ensure_ascii=False)
    
    # Print mood distribution
    print_mood_distribution(labeled_reviews)
    
    return labeled_reviews

def print_mood_distribution(labeled_reviews):
    """Print statistics about mood distribution"""
    mood_counts = {
        'work': 0, 'date': 0, 'quick_bite': 0, 'budget': 0,
        'family': 0, 'late_night': 0, 'celebration': 0
    }
    
    for review in labeled_reviews:
        for mood in review['moods']:
            if mood in mood_counts:
                mood_counts[mood] += 1
    
    print("\nMood Distribution:")
    for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mood}: {count}")

if __name__ == "__main__":
    input_file = 'data/raw/restaurant_reviews_latest.json'
    output_file = 'data/labeled/labeled_reviews.json'
    
    print("Starting synthetic labeling with Groq...")
    labeled_reviews = label_all_reviews(input_file, output_file, min_confidence=0.5)
    print(f"\nLabeled data saved to: {output_file}")