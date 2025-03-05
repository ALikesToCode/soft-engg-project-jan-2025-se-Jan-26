import axios from 'axios';
import { API_URL } from '../config';

class MonitoringService {
  constructor() {
    this.baseUrl = `${API_URL}/monitoring`;
  }

  async getDashboardData() {
    try {
      const response = await axios.get(`${this.baseUrl}/dashboard`);
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  async getSystemHealth() {
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  }

  async getSystemMetrics(history = false, limit = 10) {
    try {
      const response = await axios.get(`${this.baseUrl}/metrics`, {
        params: { history, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      throw error;
    }
  }

  async getSystemLogs(level = 'INFO', limit = 100) {
    try {
      const response = await axios.get(`${this.baseUrl}/logs`, {
        params: { level, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching system logs:', error);
      throw error;
    }
  }

  async getAlerts(type = null, severity = null, resolved = false) {
    try {
      const response = await axios.get(`${this.baseUrl}/alerts`, {
        params: { type, severity, resolved }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw error;
    }
  }

  async createAlert(alertData) {
    try {
      const response = await axios.post(`${this.baseUrl}/alerts`, alertData);
      return response.data;
    } catch (error) {
      console.error('Error creating alert:', error);
      throw error;
    }
  }

  async acknowledgeAlert(alertId, acknowledgement) {
    try {
      const response = await axios.post(
        `${this.baseUrl}/alerts/${alertId}/acknowledge`,
        acknowledgement
      );
      return response.data;
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      throw error;
    }
  }

  async resolveAlert(alertId, resolution) {
    try {
      const response = await axios.post(
        `${this.baseUrl}/alerts/${alertId}/resolve`,
        resolution
      );
      return response.data;
    } catch (error) {
      console.error('Error resolving alert:', error);
      throw error;
    }
  }

  async getServiceStatus() {
    try {
      const response = await axios.get(`${this.baseUrl}/services`);
      return response.data;
    } catch (error) {
      console.error('Error fetching service status:', error);
      throw error;
    }
  }

  async getSystemSummary() {
    try {
      const response = await axios.get(`${this.baseUrl}/summary`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system summary:', error);
      throw error;
    }
  }
}

export default new MonitoringService(); 