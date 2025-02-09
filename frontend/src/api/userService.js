import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '';

const axiosInstance = axios.create({
    baseURL: `${API_URL}${API_PREFIX}`,
    withCredentials: true,
});

export const userService = {
    // Initialize axios instance with credentials
    axiosInstance,

    // Get user profile
    async getUserProfile() {
        try {
            const response = await this.axiosInstance.get('/user/profile');
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    // Update user profile
    async updateUserProfile(userData) {
        try {
            const response = await this.axiosInstance.put('/user/profile', userData);
            return response.data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            throw error;
        }
    }
};

export default userService;
