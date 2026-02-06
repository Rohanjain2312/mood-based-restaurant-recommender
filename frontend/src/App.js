import React, { useState } from 'react';
import './App.css';
import MoodSelector from './components/MoodSelector';
import RestaurantList from './components/RestaurantList';
import MapView from './components/MapView';
import { getRecommendations } from './services/api';

function App() {
  const [selectedMood, setSelectedMood] = useState('');
  const [location, setLocation] = useState(null);
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => {
          setError('Unable to get your location. Please enable location services.');
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  };

  const handleGetRecommendations = async () => {
    if (!selectedMood) {
      setError('Please select a mood first.');
      return;
    }

    if (!location) {
      setError('Please allow location access.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getRecommendations({
        latitude: location.latitude,
        longitude: location.longitude,
        mood: selectedMood,
        radius: 3000,
        max_results: 10
      });

      setRestaurants(data.restaurants);
    } catch (err) {
      setError(err.message || 'Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Mood-Based Restaurant Recommender</h1>
        <p>Find the perfect restaurant for your mood</p>
      </header>

      <main className="App-main">
        <div className="controls">
          <MoodSelector
            selectedMood={selectedMood}
            onMoodSelect={setSelectedMood}
          />

          {!location && (
            <button className="btn btn-primary" onClick={handleGetLocation}>
              Get My Location
            </button>
          )}

          {location && (
            <button
              className="btn btn-success"
              onClick={handleGetRecommendations}
              disabled={loading || !selectedMood}
            >
              {loading ? 'Finding restaurants...' : 'Get Recommendations'}
            </button>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {location && restaurants.length > 0 && (
          <div className="results">
            <MapView
              center={{
                lat: location.latitude,
                lng: location.longitude
              }}
              restaurants={restaurants}
            />
            <RestaurantList
              restaurants={restaurants}
              mood={selectedMood}
            />
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Built with React, FastAPI, and DistilBERT</p>
        
          href="https://github.com/Rohanjain2312/mood-based-restaurant-recommender"
          target="_blank"
          rel="noopener noreferrer"
        >
          View on GitHub
        </a>
      </footer>
    </div>
  );
}

export default App;