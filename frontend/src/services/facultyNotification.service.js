import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'
import api from '@/utils/api'

// Fixing API paths by removing duplicate /api/v1/
const API_PATH_NOTIFICATIONS = '/notifications';

export const FacultyNotificationService = {
  // Get faculty notifications
  async getNotifications(filters = {}) {
    // Add timestamp to prevent caching
    const params = {
      ...filters,
      _t: Date.now()
    };
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty`, { params });
  },

  async getRecentNotifications() {
    console.log(`Inside notificationService.getRecentNotifications to send request at ${API_PATH_NOTIFICATIONS}/recent-notifications`);
    try {
      // Use params instead of headers to ensure cache-busting works
      const response = await api.get(
        `${API_PATH_NOTIFICATIONS}/recent-notifications`,
        { 
          params: { _t: Date.now() } 
        }
      );
      return response;
    } catch (error) {
      console.error("Error fetching recent notifications:", error);
      throw error;
    }
  },

  // Create a new notification
  async createNotification(notificationData) {
    console.log(`Inside notificationService.createNotification to send request at ${API_PATH_NOTIFICATIONS}/course/send`)
    try {
      // Ensure the notification has a timestamp
      const dataWithTimestamp = {
        ...notificationData,
        timestamp: notificationData.timestamp || new Date().toISOString()
      };
      
      console.log(dataWithTimestamp);
      const response = await api.post(
        `${API_PATH_NOTIFICATIONS}/course/send`,
        dataWithTimestamp
      );
      console.log("Notification Sent, Response:", response);
      return response;
    } catch (error) {
      console.error("Error sending notification:", error.response?.data || error.message);
      throw error;
    }
  },

  //Support System Notification
  async createSystemNotification(notificationData) {
    try {
      // Ensure the notification has a timestamp
      const dataWithTimestamp = {
        ...notificationData,
        timestamp: notificationData.timestamp || new Date().toISOString()
      };
      
      console.log(dataWithTimestamp);
      const response = await api.post(
        `${API_PATH_NOTIFICATIONS}/system/send`,
        dataWithTimestamp
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
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty/preferences`, {
      params: { _t: Date.now() }
    });
  },

  // Update notification preferences
  async updatePreferences(preferences) {
    return api.put(`${API_PATH_NOTIFICATIONS}/faculty/preferences`, preferences)
  },

  // Get notification statistics
  async getStatistics(courseId) {
    return api.get(`${API_PATH_NOTIFICATIONS}/faculty/statistics/${courseId}`, {
      params: { _t: Date.now() }
    });
  },

  // Mark notification as read
  async markAsRead(notificationId, type) {
    console.log(`Marking notification ${notificationId} as read`)
    return api.put(`${API_PATH_NOTIFICATIONS}/${type}/${notificationId}`, {});
  },

  // Mark all notifications as read
  async markAllAsRead(notifications) {
    console.log(`Marking multiple notifications as read: ${JSON.stringify(notifications)}`)
    return api.put(`${API_PATH_NOTIFICATIONS}/mark-all`, { notifications });
  },

  // Delete notification
  async deleteNotification(notificationId, type) {
    console.log(`Deleting notification ${notificationId} of type ${type}`)
    return api.delete(`${API_PATH_NOTIFICATIONS}/delete/${type}/${notificationId}`);
  },
  
  // Get courses for faculty
  async getCourses() {
    try {
      const response = await api.get(`${API_ROUTES.FACULTY}/courses`)
      return response.data
    } catch (error) {
      console.error('Error fetching faculty courses:', error)
      throw error
    }
  }
} 