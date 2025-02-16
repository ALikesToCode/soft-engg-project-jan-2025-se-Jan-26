import axios from 'axios';
import { API_URL } from '../config';

class MonitoringService {
  async getSystemHealth() {
    try {
      const response = await axios.get(`${API_URL}/monitoring/health`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  }

  async getPerformanceMetrics(timeRange = '24h') {
    try {
      const response = await axios.get(`${API_URL}/monitoring/performance`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  }

  async getErrorLogs(filters = {}) {
    try {
      const response = await axios.get(`${API_URL}/monitoring/errors`, {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching error logs:', error);
      throw error;
    }
  }

  async getActiveAlerts() {
    try {
      const response = await axios.get(`${API_URL}/monitoring/alerts`);
      return response.data;
    } catch (error) {
      console.error('Error fetching active alerts:', error);
      throw error;
    }
  }

  async dismissAlert(alertId) {
    try {
      const response = await axios.post(`${API_URL}/monitoring/alerts/${alertId}/dismiss`);
      return response.data;
    } catch (error) {
      console.error('Error dismissing alert:', error);
      throw error;
    }
  }

  async getResourceUsage() {
    try {
      const response = await axios.get(`${API_URL}/monitoring/resources`);
      return response.data;
    } catch (error) {
      console.error('Error fetching resource usage:', error);
      throw error;
    }
  }

  async getEndpointPerformance() {
    try {
      const response = await axios.get(`${API_URL}/monitoring/endpoints`);
      return response.data;
    } catch (error) {
      console.error('Error fetching endpoint performance:', error);
      throw error;
    }
  }

  async exportLogs(filters = {}) {
    try {
      const response = await axios.get(`${API_URL}/monitoring/logs/export`, {
        params: filters,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting logs:', error);
      throw error;
    }
  }

  async resolveError(errorId) {
    try {
      const response = await axios.post(`${API_URL}/monitoring/errors/${errorId}/resolve`);
      return response.data;
    } catch (error) {
      console.error('Error resolving error:', error);
      throw error;
    }
  }

  async getSystemMetrics() {
    try {
      const response = await axios.get(`${API_URL}/monitoring/metrics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      throw error;
    }
  }

  // WebSocket connection for real-time updates
  setupWebSocket() {
    try {
      const ws = new WebSocket(`${API_URL.replace('http', 'ws')}/monitoring/ws`);
      
      ws.onopen = () => {
        console.log('WebSocket connection established');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Handle different types of real-time updates
        switch (data.type) {
          case 'health':
            this.handleHealthUpdate(data);
            break;
          case 'alert':
            this.handleAlertUpdate(data);
            break;
          case 'performance':
            this.handlePerformanceUpdate(data);
            break;
          default:
            console.log('Received unknown update type:', data.type);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
        // Implement reconnection logic here
        setTimeout(() => this.setupWebSocket(), 5000);
      };

      return ws;
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
      throw error;
    }
  }

  // Helper methods for WebSocket updates
  handleHealthUpdate(data) {
    // Implement health update logic
    console.log('Health update received:', data);
  }

  handleAlertUpdate(data) {
    // Implement alert update logic
    console.log('Alert update received:', data);
  }

  handlePerformanceUpdate(data) {
    // Implement performance update logic
    console.log('Performance update received:', data);
  }
}

export default new MonitoringService(); 