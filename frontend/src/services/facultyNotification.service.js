import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'
import api from '@/utils/api'

// Fixing API paths by removing duplicate /api/v1/
const API_PATH_NOTIFICATIONS = '/notifications';

export const FacultyNotificationService = {
  // Get faculty notifications
  async getNotifications(filters = {}) {
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty`, { params: filters })
  },

  async getRecentNotifications(headers) {
    console.log(`Inside notificationService.getRecentNotifications to send request at ${API_PATH_NOTIFICATIONS}/recent-notifications`)
    try {
      const response = await api.get(
        `${API_PATH_NOTIFICATIONS}/recent-notifications`,
        headers
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Create a new notification
  async createNotification(notificationData, headers) {
    console.log(`Inside notificationService.createNotification to send request at ${API_PATH_NOTIFICATIONS}/course/send`)
    try {
      console.log(notificationData)
      const response = await api.post(
        `${API_PATH_NOTIFICATIONS}/course/send`,
        notificationData,
        headers
      );
      console.log("Notification Sent, Response:", response);
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
        `${API_PATH_NOTIFICATIONS}/system/send`,
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
    return api.put(`${API_PATH_NOTIFICATIONS}/faculty/${notificationId}/status`, { status })
  },

  // Get notification preferences
  async getPreferences() {
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty/preferences`)
  },

  // Update notification preferences
  async updatePreferences(preferences) {
    return api.put(`${API_PATH_NOTIFICATIONS}/faculty/preferences`, preferences)
  },

  // Get notification statistics
  async getStatistics(courseId) {
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty/statistics/${courseId}`)
  },

  // Mark notification as read
  async markAsRead(notificationId) {
    return api.put(`${API_PATH_NOTIFICATIONS}/faculty/${notificationId}/read`)
  },

  // Delete notification
  async deleteNotification(notificationId) {
    return api.delete(`${API_PATH_NOTIFICATIONS}/faculty/${notificationId}`)
  }
} 