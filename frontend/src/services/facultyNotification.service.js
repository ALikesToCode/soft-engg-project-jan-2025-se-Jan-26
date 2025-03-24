import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'
import api from '@/utils/api'

export const FacultyNotificationService = {
  // Get faculty notifications
  async getNotifications(filters = {}) {
    return axios.get(`${API_ROUTES.NOTIFICATIONS}/faculty`, { params: filters })
  },

  // Create a new notification
  async createNotification(notificationData, headers) {
    console.log(`Inside notificationService.createNotification to send request at ${API_ROUTES.NOTIFICATIONS}/course/send`)
    try {
      console.log(notificationData)
      const response = await api.post(
        `${API_ROUTES.NOTIFICATIONS}/course/send`,
        notificationData,
        headers
      );
      return response;
    } catch (error) {
      console.error("Error sending notification:", error.response?.data || error.message);
      throw error;
    }
  },

  //Support System Notification
  async createSystemNotification(notificationData, headers) {
    try {
      console.log(notificationData)
      const response = await api.post(
        `${API_ROUTES.NOTIFICATIONS}/system/send`,
        notificationData,
        headers
      );
      return response;
    } catch (error) {
      console.error("Error sending system notification:", error.response?.data || error.message);
      throw error;

    }
  },

  // Update notification status
  async updateNotificationStatus(notificationId, status) {
    return axios.put(`${API_ROUTES.NOTIFICATIONS}/faculty/${notificationId}/status`, { status })
  },

  // Get notification preferences
  async getPreferences() {
    return axios.get(`${API_ROUTES.NOTIFICATIONS}/faculty/preferences`)
  },

  // Update notification preferences
  async updatePreferences(preferences) {
    return axios.put(`${API_ROUTES.NOTIFICATIONS}/faculty/preferences`, preferences)
  },

  // Get notification statistics
  async getStatistics(courseId) {
    return axios.get(`${API_ROUTES.NOTIFICATIONS}/faculty/statistics/${courseId}`)
  },

  // Mark notification as read
  async markAsRead(notificationId) {
    return axios.put(`${API_ROUTES.NOTIFICATIONS}/faculty/${notificationId}/read`)
  },

  // Delete notification
  async deleteNotification(notificationId) {
    return axios.delete(`${API_ROUTES.NOTIFICATIONS}/faculty/${notificationId}`)
  }
} 