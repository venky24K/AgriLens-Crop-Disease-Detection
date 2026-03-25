import axios from 'axios';

// During local development, use the desktop IP or localhost
// For production (Render), this should be the deployed API URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;
