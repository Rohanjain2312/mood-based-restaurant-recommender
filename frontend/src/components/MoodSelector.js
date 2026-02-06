import React from 'react';
import './MoodSelector.css';

const MOODS = [
  { value: 'celebration', label: 'Celebration', icon: '🎉', description: 'Special occasions, upscale' },
  { value: 'date', label: 'Date', icon: '❤️', description: 'Romantic, intimate atmosphere' },
  { value: 'quick_bite', label: 'Quick Bite', icon: '⚡', description: 'Fast service, casual' },
  { value: 'budget', label: 'Budget', icon: '💰', description: 'Affordable, good value' }
];

function MoodSelector({ selectedMood, onMoodSelect }) {
  return (
    <div className="mood-selector">
      <h2>What's your mood?</h2>
      <div className="mood-grid">
        {MOODS.map(mood => (
          <button
            key={mood.value}
            className={`mood-card ${selectedMood === mood.value ? 'selected' : ''}`}
            onClick={() => onMoodSelect(mood.value)}
          >
            <div className="mood-icon">{mood.icon}</div>
            <div className="mood-label">{mood.label}</div>
            <div className="mood-description">{mood.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default MoodSelector;