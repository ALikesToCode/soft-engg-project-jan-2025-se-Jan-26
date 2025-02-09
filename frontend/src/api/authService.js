import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '';

const axiosInstance = axios.create({
    baseURL: `${API_URL}${API_PREFIX}`,
    withCredentials: true,
});

export const authService = {
    // Initialize axios instance with credentials
    axiosInstance,

    // Login with Google
    async loginWithGoogle() {
        window.location.href = `${API_URL}${API_PREFIX}/auth/login`;
    },

    // Get current user
    async getCurrentUser() {
        try {
            const response = await this.axiosInstance.get('/auth/me');
            return response.data;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    },

    // Check if user is authenticated
    async isAuthenticated() {
        try {
            const user = await this.getCurrentUser();
            return !!user;
        } catch {
            return false;
        }
    },

    // Logout
    async logout() {
        try {
            await this.axiosInstance.post('/auth/logout');
            localStorage.removeItem('user');
            window.location.href = '/';
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }
};

export default authService;
