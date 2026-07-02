// Central API base URL configuration.
// In production on Render, set the environment variable:
//   VITE_API_BASE_URL=https://your-backend-name.onrender.com
// In local development this falls back to the Vite proxy (/api -> localhost:8000)
let base = import.meta.env.VITE_API_BASE_URL || '/api';

// If VITE_API_BASE_URL is a raw hostname (from Render BlueprintSpecs host property), prepend https://
if (base !== '/api' && !base.startsWith('http://') && !base.startsWith('https://')) {
  base = `https://${base}`;
}

const API_BASE = base;

export default API_BASE;
