// Central API base URL configuration.
// In production on Render, set the environment variable:
//   VITE_API_BASE_URL=https://your-backend-name.onrender.com
// In local development this falls back to the Vite proxy (/api -> localhost:8000)
const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}`
  : '/api';

export default API_BASE;
