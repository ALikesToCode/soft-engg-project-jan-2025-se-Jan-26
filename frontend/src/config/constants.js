// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Chat Configuration
export const CHAT_POLL_INTERVAL = 10000 // 10 seconds

// Authentication
export const TOKEN_EXPIRY_BUFFER = 300000 // 5 minutes in ms before token expiry to refresh

// UI Configuration
export const NOTIFICATION_DURATION = 5000 // 5 seconds
export const MAX_MOBILE_WIDTH = 768 // Width in pixels to consider a mobile device

// Feature Flags
export const FEATURES = {
  CHAT_ENABLED: true,
  NOTIFICATIONS_ENABLED: true,
  ACADEMIC_INTEGRITY_CHECK: true
} 