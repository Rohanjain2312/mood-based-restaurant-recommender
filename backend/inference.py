import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from typing import List, Dict
import os

class MoodClassifier:
    """
    Wrapper class for mood classification inference
    """
    
    def __init__(self, model_path: str, device: str = None):
        """
        Initialize classifier with trained model
        
        Args:
            model_path: Path to saved model directory
            device: 'cuda', 'cpu', or None (auto-detect)
        """
        self.moods = ['date', 'quick_bite', 'budget', 'celebration']
        self.num_labels = len(self.moods)
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Load tokenizer and model
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        print(f'Model loaded from {model_path} on {self.device}')
    
    def predict_single(self, text: str, threshold: float = 0.5) -> Dict[str, float]:
        """
        Classify a single review
        
        Args:
            text: Review text
            threshold: Classification threshold (default 0.5)
        
        Returns:
            Dictionary mapping mood to probability
        """
        # Tokenize
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()[0]
        
        # Create mood probability dictionary
        mood_probs = {mood: float(prob) for mood, prob in zip(self.moods, probs)}
        
        return mood_probs
    
    def predict_batch(self, texts: List[str], threshold: float = 0.5) -> List[Dict[str, float]]:
        """
        Classify multiple reviews efficiently
        
        Args:
            texts: List of review texts
            threshold: Classification threshold
        
        Returns:
            List of dictionaries mapping mood to probability
        """
        # Tokenize batch
        encodings = self.tokenizer(
            texts,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()
        
        # Create list of mood probability dictionaries
        results = []
        for prob_vector in probs:
            mood_probs = {mood: float(prob) for mood, prob in zip(self.moods, prob_vector)}
            results.append(mood_probs)
        
        return results
    
    def aggregate_mood_scores(self, reviews: List[str], target_mood: str) -> float:
        """
        Aggregate mood scores across multiple reviews for a restaurant
        
        Args:
            reviews: List of review texts for a restaurant
            target_mood: The mood to score for
        
        Returns:
            Aggregated mood score (0-10 scale)
        """
        if not reviews:
            return 0.0
        
        # Get predictions for all reviews
        predictions = self.predict_batch(reviews)
        
        # Extract target mood probabilities
        mood_probs = [pred[target_mood] for pred in predictions]
        
        # Calculate average probability
        avg_prob = np.mean(mood_probs)
        
        # Scale to 0-10
        mood_score = avg_prob * 10
        
        return round(mood_score, 2)

def load_classifier(model_path: str = 'models/distilbert-mood-classifier') -> MoodClassifier:
    """
    Convenience function to load classifier
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    return MoodClassifier(model_path)

if __name__ == "__main__":
    # Test inference
    classifier = load_classifier()
    
    test_reviews = [
        "Great place to work on my laptop. Fast WiFi and plenty of outlets.",
        "Perfect romantic dinner spot. Dim lighting and intimate atmosphere.",
        "Quick service, got my food in 5 minutes. Perfect for lunch break."
    ]
    
    print("Testing inference...")
    for review in test_reviews:
        result = classifier.predict_single(review)
        print(f"\nReview: {review[:50]}...")
        print("Mood probabilities:")
        for mood, prob in sorted(result.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mood}: {prob:.3f}")