import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import './MapView.css';

const containerStyle = {
  width: '100%',
  height: '400px',
  borderRadius: '12px'
};

function MapView({ center, restaurants }) {
  return (
    <div className="map-view">
      <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={center}
          zoom={14}
        >
          <Marker
            position={center}
            icon={{
              url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            }}
            title="Your Location"
          />

          {restaurants.map((restaurant, index) => (
            <Marker
              key={restaurant.place_id}
              position={{
                lat: restaurant.latitude || center.lat,
                lng: restaurant.longitude || center.lng
              }}
              label={{
                text: `${index + 1}`,
                color: 'white',
                fontWeight: 'bold'
              }}
              title={restaurant.name}
            />
          ))}
        </GoogleMap>
      </LoadScript>
    </div>
  );
}

export default MapView;