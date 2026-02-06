import React from 'react';
import './RestaurantCard.css';

function RestaurantCard({ restaurant, rank }) {
  const getMoodScoreColor = (score) => {
    if (score >= 8) return '#4CAF50';
    if (score >= 6) return '#FF9800';
    return '#F44336';
  };

  const openGoogleMaps = () => {
    window.open(
      `https://www.google.com/maps/place/?q=place_id:${restaurant.place_id}`,
      '_blank'
    );
  };

  return (
    <div className="restaurant-card">
      <div className="card-header">
        <div className="rank-badge">#{rank}</div>
        <div
          className="mood-score"
          style={{ backgroundColor: getMoodScoreColor(restaurant.mood_score) }}
        >
          {restaurant.mood_score}/10
        </div>
      </div>

      <h3 className="restaurant-name">{restaurant.name}</h3>
      <p className="restaurant-address">{restaurant.address}</p>

      <div className="restaurant-info">
        <div className="info-item">
          <span className="info-label">Rating:</span>
          <span className="info-value">
            ⭐ {restaurant.rating} ({restaurant.user_ratings_total} reviews)
          </span>
        </div>

        {restaurant.price_level && (
          <div className="info-item">
            <span className="info-label">Price:</span>
            <span className="info-value">
              {'$'.repeat(restaurant.price_level)}
            </span>
          </div>
        )}

        {restaurant.is_open !== null && (
          <div className="info-item">
            <span className="info-label">Status:</span>
            <span className={`status ${restaurant.is_open ? 'open' : 'closed'}`}>
              {restaurant.is_open ? 'Open Now' : 'Closed'}
            </span>
          </div>
        )}
      </div>

      <button className="view-on-maps-btn" onClick={openGoogleMaps}>
        View on Google Maps
      </button>
    </div>
  );
}

export default RestaurantCard;