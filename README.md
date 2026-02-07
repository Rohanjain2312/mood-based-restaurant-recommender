# Mood-Based Restaurant Recommender

A machine learning application that analyzes restaurant reviews to recommend venues matching specific dining moods using a fine-tuned DistilBERT model.

## Links

- **Live Demo**: [HuggingFace Spaces](https://huggingface.co/spaces/rohanjain2312/restaurant-mood-recommender)
- **Model**: [HuggingFace Hub](https://huggingface.co/rohanjain2312/distilbert-mood-classifier)
- **Training Notebooks**: [GitHub](https://github.com/Rohanjain2312/mood-based-restaurant-recommender/tree/main/notebooks)

### Using the Application

1. Select a city from the dropdown (30 major cities available)
2. Choose a mood category (celebration, date, quick_bite, budget)
3. Click "Find Restaurants" to get ranked recommendations
4. Results display mood scores, ratings, and clickable Google Maps links

## Key Features

- Multi-label text classification across 4 mood categories
- Real-time restaurant discovery via Google Places API
- Review-based scoring system (0-10 scale) using ML inference
- Support for 30 major cities worldwide
- Interactive web interface built with Gradio

## Model Performance

The model was trained on 227 labeled restaurant reviews and evaluated on a held-out test set:

| Mood Category | Precision | Recall | F1-Score |
|--------------|-----------|--------|----------|
| Celebration  | 1.00      | 0.83   | 0.91     |
| Quick Bite   | 0.70      | 0.88   | 0.78     |
| Date         | 0.78      | 0.47   | 0.58     |
| Budget       | 0.40      | 0.57   | 0.47     |

**Overall Metrics**: Macro F1 = 0.69 | Micro F1 = 0.75

## Technical Architecture

### Data Pipeline
1. **Collection**: Google Places API scraping across 5 US cities (NYC, LA, SF, Boston, Seattle)
2. **Labeling**: Synthetic labeling using Groq's Llama 3.1 API with confidence thresholding
3. **Processing**: Multi-label binary encoding for 4 mood categories

### Model Training
- **Base Model**: DistilBERT (distilbert-base-uncased)
- **Task**: Multi-label sequence classification
- **Training Time**: 48 minutes on Google Colab (T4 GPU)
- **Hyperparameters**:
  - Learning rate: 2e-5 with linear warmup (100 steps)
  - Batch size: 16
  - Epochs: 4 with early stopping (patience=2)
  - Loss function: BCEWithLogitsLoss with class weights
  - Optimizer: AdamW
  - Gradient clipping: max_norm=1.0

### Deployment
- **Backend**: Gradio web framework
- **Model Hosting**: HuggingFace Hub
- **API Integration**: Google Places API for restaurant data
- **Inference**: PyTorch with CPU support

## Repository Structure
```
mood-based-restaurant-recommender/
├── app.py                          # Gradio application interface
├── inference.py                    # Model inference wrapper class
├── requirements.txt                # Python dependencies
├── data/
│   └── labeled/
│       └── labeled_reviews.json    # Training dataset (227 samples)
├── notebooks/
│   ├── 02_model_training.ipynb     # Model training pipeline
│   └── 03_model_evaluation.ipynb  # Performance analysis
└── scripts/
    ├── collect_reviews.py          # Google Places API scraper
    └── label_reviews.py            # Groq API synthetic labeling
```

## Dataset Statistics

- **Total Reviews Collected**: 1,320 from 300 restaurants
- **Labeled Reviews**: 560 via Groq API (1 hour processing time)
- **Training Set**: 227 reviews after quality filtering
- **Mood Distribution**:
  - Celebration: 180 samples
  - Date: 103 samples
  - Quick Bite: 40 samples
  - Budget: 37 samples

## Installation & Usage

### Prerequisites
- Python 3.11+
- Google Places API key
- HuggingFace account (for model access)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Rohanjain2312/mood-based-restaurant-recommender.git
cd mood-based-restaurant-recommender
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file
echo "GOOGLE_PLACES_API_KEY=your_api_key_here" > .env
```

4. Run the application:
```bash
python app.py
```

5. Open browser at `http://localhost:7860`


## Model Training

To retrain the model:

1. Open `notebooks/02_model_training.ipynb` in Google Colab
2. Upload the labeled dataset from `data/labeled/`
3. Run all cells to train and save the model
4. Download the trained model or push directly to HuggingFace Hub

The notebook includes:
- Data preprocessing and train/validation/test splitting
- Custom DistilBERT architecture with multi-label classification head
- Training loop with validation monitoring
- Model checkpointing and metric logging

## API Reference

### MoodClassifier Class
```python
from inference import MoodClassifier

# Initialize classifier
classifier = MoodClassifier('rohanjain2312/distilbert-mood-classifier')

# Single review prediction
result = classifier.predict_single("Great romantic atmosphere!")
# Returns: {'celebration': 0.23, 'date': 0.87, 'quick_bite': 0.12, 'budget': 0.31}

# Batch prediction
results = classifier.predict_batch([review1, review2, review3])

# Aggregate mood score for restaurant
score = classifier.aggregate_mood_scores(review_list, target_mood='date')
# Returns: 8.7 (on 0-10 scale)
```

## Limitations

- Google Places API returns maximum 5 reviews per restaurant
- Model performance varies by mood category due to class imbalance
- Requires minimum 3 reviews per restaurant for scoring
- Limited to 30 predefined cities (no arbitrary location support in current version)

## Future Improvements

- Implement FastAPI + React frontend for geolocation support
- Expand training dataset with web scraping from additional review platforms
- Add more mood categories (family-friendly, work meetings, etc.)
- Implement user feedback loop for model refinement
- Add multilingual support for international cities


## Author

**Rohan Jain**  
Master's in Applied Machine Learning, University of Maryland (Expected 2026)  
Former BI Associate at Goldman Sachs

- LinkedIn: [linkedin.com/in/jaroh23](https://www.linkedin.com/in/jaroh23/)
- GitHub: [github.com/Rohanjain2312](https://github.com/Rohanjain2312)
- HuggingFace: [huggingface.co/rohanjain2312](https://huggingface.co/rohanjain2312)

## Acknowledgments

- Google Places API for restaurant data and review access
- Groq API (Llama 3.1) for efficient synthetic labeling
- Anthropic Claude for development assistance and code optimization
- HuggingFace for model hosting and deployment infrastructure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this project in your research or application, please cite:
```bibtex
@software{jain2026mood,
  author = {Jain, Rohan},
  title = {Mood-Based Restaurant Recommender},
  year = {2026},
  url = {https://github.com/Rohanjain2312/mood-based-restaurant-recommender}
}
```