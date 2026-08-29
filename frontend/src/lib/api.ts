import axios from 'axios';

export const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
});

// Setup simple auth token injection if we had one, but we'll mock it for now.
api.interceptors.request.use((config) => {
  // Hardcoded test JWT or simple authorization header
  config.headers.Authorization = `Bearer test-analyst-token`;
  return config;
});
