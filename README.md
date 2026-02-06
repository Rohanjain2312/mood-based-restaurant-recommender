# Mood-Based Restaurant Recommender

An intelligent restaurant recommendation system that uses NLP to classify restaurant reviews by mood and provides personalized suggestions based on user preferences.

## Features

- Multi-label mood classification (work, date, quick_bite, budget, family, late_night, celebration)
- Fine-tuned DistilBERT model on 1000+ restaurant reviews
- Real-time restaurant discovery using Google Places API
- Review aggregation and mood scoring (0-10 scale)
- RESTful API backend with FastAPI
- Interactive React frontend with Google Maps integration

## Tech Stack

**Machine Learning:**
- PyTorch
- Transformers (DistilBERT)
- Scikit-learn
- Groq API (synthetic labeling)

**Backend:**
- FastAPI
- Python 3.8+
- Google Places API

**Frontend:**
- React
- Google Maps JavaScript API
- Axios

**Deployment:**
- Heroku/Railway (backend)
- Vercel/Netlify (frontend)
- HuggingFace Hub (model hosting)

## Project Structure
```
mood-based-restaurant-recommender/
├── data/
│   ├── raw/                    # Raw scraped reviews
│   └── labeled/                # Synthetically labeled data
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_model_evaluation.ipynb
├── models/
│   └── distilbert-mood-classifier/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── inference.py           # Model inference logic
│   └── requirements.txt
├── frontend/
│   └── (React application)
├── scripts/
│   ├── collect_reviews.py
│   └── label_reviews.py
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Cloud Platform account (for Places API)
- Groq API key (for synthetic labeling)

### Backend Setup

1. Clone repository:
```bash
git clone https://github.com/Rohanjain2312/mood-based-restaurant-recommender.git
cd mood-based-restaurant-recommender
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Add your API keys to .env
```

5. Run backend:
```bash
cd backend
python app.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

## Data Collection

Collect restaurant reviews from Google Places API:
```bash
python scripts/collect_reviews.py
```

This scrapes reviews from 5 major cities (NYC, Boston, SF, LA, Seattle) targeting restaurants with:
- Rating > 3.9
- User ratings > 50
- Minimum 10 reviews

## Synthetic Labeling

Label collected reviews using Groq API:
```bash
python scripts/label_reviews.py
```

This uses `llama-3.1-8b-instant` to classify reviews into 7 mood categories with confidence scores.

## Model Training

Open `notebooks/02_model_training.ipynb` in Google Colab:

1. Upload notebook to Colab
2. Clone this repository in Colab
3. Run all cells to train DistilBERT classifier
4. Download trained model from Google Drive

## Model Performance

| Mood | Precision | Recall | F1-Score |
|------|-----------|--------|----------|
| work | TBD | TBD | TBD |
| date | TBD | TBD | TBD |
| quick_bite | TBD | TBD | TBD |
| budget | TBD | TBD | TBD |
| family | TBD | TBD | TBD |
| late_night | TBD | TBD | TBD |
| celebration | TBD | TBD | TBD |

**Overall:** Macro F1 = TBD | Micro F1 = TBD

## API Documentation

### Endpoints

**GET /** - Health check
```json
{
  "message": "Mood-Based Restaurant Recommender API",
  "status": "healthy",
  "version": "1.0.0"
}
```

**POST /recommend** - Get restaurant recommendations

Request:
```json
{
  "latitude": 40.7580,
  "longitude": -73.9855,
  "mood": "date",
  "radius": 3000,
  "max_results": 10
}
```

Response:
```json
{
  "mood": "date",
  "restaurants": [
    {
      "place_id": "ChIJ...",
      "name": "Romantic Restaurant",
      "address": "123 Main St",
      "rating": 4.5,
      "user_ratings_total": 250,
      "mood_score": 8.7,
      "is_open": true,
      "price_level": 3,
      "types": ["restaurant", "food"]
    }
  ],
  "total_found": 15
}
```

## Deployment

### Backend (Heroku)
```bash
heroku create mood-restaurant-api
git push heroku main
heroku config:set GOOGLE_PLACES_API_KEY=your_key
```

### Frontend (Vercel)
```bash
vercel deploy
```

### Model (HuggingFace)
```bash
huggingface-cli login
huggingface-cli upload Rohanjain2312/distilbert-mood-classifier models/distilbert-mood-classifier/
```

## Future Improvements

- [ ] Add user preference learning (collaborative filtering)
- [ ] Implement caching for frequent queries
- [ ] Add more mood categories
- [ ] Support cuisine-specific filtering
- [ ] Multi-language support
- [ ] Mobile app (React Native)

## Contributing

Pull requests welcome. For major changes, open an issue first.

## License

MIT

## Contact

Rohan Jain - [GitHub](https://github.com/Rohanjain2312) | [LinkedIn](https://linkedin.com/in/rohanjain2312)

Project Link: https://github.com/Rohanjain2312/mood-based-restaurant-recommender
```

**Create `.env.example`:**
```
# Google Places API
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Groq API (for synthetic labeling)
GROQ_API_KEY=your_groq_api_key_here

# Model settings
MODEL_PATH=models/distilbert-mood-classifier

# API settings
API_HOST=0.0.0.0
API_PORT=8000