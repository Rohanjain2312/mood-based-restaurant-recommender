import React from 'react';
import RestaurantCard from './RestaurantCard';
import './RestaurantList.css';

function RestaurantList({ restaurants, mood }) {
  if (!restaurants || restaurants.length === 0) {
    return null;
  }

  return (
    <div className="restaurant-list">
      <h2>Top Recommendations for {mood}</h2>
      <p className="results-count">Found {restaurants.length} restaurants</p>
      <div className="restaurant-cards">
        {restaurants.map((restaurant, index) => (
          <RestaurantCard
            key={restaurant.place_id}
            restaurant={restaurant}
            rank={index + 1}
          />
        ))}
      </div>
    </div>
  );
}

export default RestaurantList;