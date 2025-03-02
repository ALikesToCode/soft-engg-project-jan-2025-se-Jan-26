import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '';

/**
 * Axios instance configured with the base URL and credentials
 * @type {import('axios').AxiosInstance}
 */
const axiosInstance = axios.create({
    baseURL: `${API_URL}${API_PREFIX}`,
    withCredentials: true,
});

/**
 * Service for handling user profile operations
 * @namespace userService
 */
export const userService = {
    /**
     * Axios instance with proper configuration for API requests
     * @memberof userService
     * @type {import('axios').AxiosInstance}
     */
    axiosInstance,

    /**
     * Retrieves the current user's profile information
     * 
     * @memberof userService
     * @async
     * @function getUserProfile
     * @returns {Promise<Object>} User profile data including id, name, email, role, and picture
     * @throws {Error} If the API request fails
     * 
     * @example
     * // Get the current user's profile
     * try {
     *   const profile = await userService.getUserProfile();
     *   console.log(profile);
     * } catch (error) {
     *   console.error('Failed to get profile:', error);
     * }
     */
    async getUserProfile() {
        try {
            const response = await this.axiosInstance.get('/user/profile');
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    /**
     * Updates the current user's profile information
     * 
     * @memberof userService
     * @async
     * @function updateUserProfile
     * @param {Object} userData - The user data to update
     * @param {string} [userData.name] - The user's display name
     * @param {string} [userData.email] - The user's email address
     * @param {string} [userData.picture] - URL to the user's profile picture
     * @returns {Promise<Object>} Updated user profile data
     * @throws {Error} If the API request fails
     * 
     * @example
     * // Update the user's name
     * try {
     *   const updatedProfile = await userService.updateUserProfile({ name: 'New Name' });
     *   console.log(updatedProfile);
     * } catch (error) {
     *   console.error('Failed to update profile:', error);
     * }
     */
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
