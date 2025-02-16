import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'

export const FacultyNotificationService = {
  // Get faculty notifications
  async getNotifications(filters = {}) {
    return axios.get(`${API_ROUTES.NOTIFICATIONS}/faculty`, { params: filters })
  },

  // Create a new notification
  async createNotification(notificationData) {
    return axios.post(`${API_ROUTES.NOTIFICATIONS}/faculty`, notificationData)
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