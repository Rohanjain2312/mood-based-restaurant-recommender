import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRecommendations = async (params) => {
  try {
    const response = await apiClient.post('/recommend', params);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Server error occurred');
    } else if (error.request) {
      throw new Error('Unable to connect to server. Please try again.');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
};

export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
};