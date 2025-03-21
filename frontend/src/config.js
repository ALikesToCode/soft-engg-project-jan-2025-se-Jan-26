// API Configuration
export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + 
                     (import.meta.env.VITE_API_PREFIX || '/api/v1');

// Other configuration constants can be added here
export const DEFAULT_TIMEOUT = 30000; // 30 seconds
export const REFRESH_INTERVAL = 60000; // 1 minute 