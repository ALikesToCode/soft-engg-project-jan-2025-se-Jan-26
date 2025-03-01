import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '';
const isDev = import.meta.env.MODE === 'development';

// Enable more verbose logging in development mode
const logLevel = isDev ? 'debug' : 'error';

// Custom logger with different log levels
const logger = {
    debug: (...args) => isDev && console.debug('[Auth Service]', ...args),
    log: (...args) => console.log('[Auth Service]', ...args),
    warn: (...args) => console.warn('[Auth Service]', ...args),
    error: (...args) => console.error('[Auth Service]', ...args),
};

const axiosInstance = axios.create({
    baseURL: `${API_URL}${API_PREFIX}`,
    withCredentials: true,
});

// Add request interceptor to include the token in every request
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            // Remove quotes if token is stored as JSON string
            const cleanToken = token.replace(/^"|"$/g, '');
            config.headers.Authorization = `Bearer ${cleanToken}`;
            logger.debug(`Request to ${config.url} - Adding Authorization header: Bearer ${cleanToken.substring(0, 15)}...`);
        } else {
            logger.warn(`Request to ${config.url} - No token found`);
        }
        
        // Log request details in development
        if (isDev) {
            logger.debug(`Request: ${config.method.toUpperCase()} ${config.url}`, config.data || {});
        }
        
        return config;
    },
    (error) => {
        logger.error('Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for debugging
axiosInstance.interceptors.response.use(
    (response) => {
        logger.debug(`Response from ${response.config.url}: ${response.status}`, 
            isDev ? response.data : '');
        return response;
    },
    (error) => {
        if (error.response) {
            logger.error(`Response error from ${error.config?.url || 'unknown'}: ${error.response.status}`, 
                error.response.data);
                
            // Handle 401 errors (unauthorized)
            if (error.response.status === 401) {
                logger.warn('Unauthorized access detected - token may be invalid or expired');
                // We could trigger a token refresh here if needed
            }
        } else if (error.request) {
            logger.error('No response received:', error.request);
        } else {
            logger.error('Request error:', error.message);
        }
        return Promise.reject(error);
    }
);

export const authService = {
    // Initialize axios instance with credentials
    axiosInstance,

    // Login with Google
    async loginWithGoogle() {
        // Redirect to the backend's Google login endpoint
        const redirectUrl = `${API_URL}${API_PREFIX}/auth/login/google`;
        logger.log('Redirecting to Google login:', redirectUrl);
        window.location.href = redirectUrl;
    },

    // Get current user
    async getCurrentUser() {
        try {
            logger.log('Getting current user...');
            // Check if token exists before making the request
            const token = localStorage.getItem('token');
            if (!token) {
                logger.warn('No token found in localStorage');
                return null;
            }
            
            // Log token details in development mode
            if (isDev) {
                this.debugTokenStatus();
            }
            
            const response = await this.axiosInstance.get('/auth/me');
            logger.log('Current user data retrieved successfully');
            logger.debug('User data:', response.data);
            return response.data;
        } catch (error) {
            logger.error('Error getting current user:', error.message);
            if (error.response) {
                logger.error(`Status: ${error.response.status}, Data:`, error.response.data);
                
                // If unauthorized, clear token
                if (error.response.status === 401) {
                    logger.warn('Unauthorized - clearing invalid token');
                    localStorage.removeItem('token');
                }
            }
            return null;
        }
    },

    // Check if user is authenticated
    async isAuthenticated() {
        try {
            logger.debug('Checking authentication status...');
            const user = await this.getCurrentUser();
            const isAuth = !!user;
            logger.debug(`Authentication check result: ${isAuth ? 'Authenticated' : 'Not authenticated'}`);
            return isAuth;
        } catch (error) {
            logger.error('Error checking authentication:', error.message);
            return false;
        }
    },

    // Refresh token
    async refreshToken() {
        try {
            logger.log('Attempting to refresh token...');
            const token = localStorage.getItem('token');
            
            if (!token) {
                logger.warn('Cannot refresh - no token found');
                return false;
            }
            
            const response = await this.axiosInstance.post('/auth/refresh');
            
            if (response.data && response.data.access_token) {
                logger.log('Token refreshed successfully');
                localStorage.setItem('token', response.data.access_token);
                return true;
            } else {
                logger.warn('Token refresh response missing access_token');
                return false;
            }
        } catch (error) {
            logger.error('Error refreshing token:', error.message);
            if (error.response && error.response.status === 401) {
                logger.warn('Token refresh failed - clearing invalid token');
                localStorage.removeItem('token');
            }
            return false;
        }
    },

    // Logout
    async logout() {
        try {
            logger.log('Logging out user...');
            await this.axiosInstance.get('/auth/logout');
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            logger.log('Logout successful, redirecting to home');
            window.location.href = '/';
        } catch (error) {
            logger.error('Error during logout:', error.message);
            // Force logout even if the API call fails
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            window.location.href = '/';
        }
    },

    // Debug token status - useful for troubleshooting
    debugTokenStatus() {
        const token = localStorage.getItem('token');
        logger.log('Token exists:', !!token);
        
        if (!token) {
            return false;
        }
        
        try {
            // Try to parse if it's stored as JSON
            let tokenValue = token;
            try {
                const parsedToken = JSON.parse(token);
                if (typeof parsedToken === 'string') {
                    tokenValue = parsedToken;
                    logger.debug('Token is stored as JSON string');
                } else {
                    logger.debug('Token is stored as JSON object');
                    return !!token;
                }
            } catch (e) {
                // Not JSON, just a string
                logger.debug('Token is stored as plain string');
            }
            
            // Show token details
            const tokenParts = tokenValue.split('.');
            if (tokenParts.length === 3) {
                try {
                    // Decode the payload (middle part)
                    const payload = JSON.parse(atob(tokenParts[1]));
                    const expiry = payload.exp ? new Date(payload.exp * 1000) : 'unknown';
                    const isExpired = payload.exp ? Date.now() > payload.exp * 1000 : false;
                    
                    logger.debug('Token details:', {
                        subject: payload.sub || 'unknown',
                        expiry: expiry.toString(),
                        isExpired,
                        timeRemaining: payload.exp ? 
                            Math.floor((payload.exp * 1000 - Date.now()) / 1000) + ' seconds' : 
                            'unknown'
                    });
                    
                    return !isExpired;
                } catch (e) {
                    logger.warn('Failed to decode token payload:', e.message);
                }
            } else {
                logger.warn('Token does not appear to be in JWT format (missing 3 parts)');
            }
        } catch (e) {
            logger.error('Error analyzing token:', e.message);
        }
        
        return !!token;
    },
    
    // Clear all auth data (for testing/debugging)
    clearAuthData() {
        logger.warn('Clearing all authentication data');
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        return true;
    }
};

export default authService;
