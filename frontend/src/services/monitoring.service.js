import axios from 'axios';
import { API_URL } from '../config';

class MonitoringService {
  // Helper to get current auth token
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Check if user is authenticated with token
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  // Check if the current user has the support role
  hasSupportRole() {
    // Get user role from localStorage (set during login)
    const userRole = localStorage.getItem('userRole');
    return userRole === 'SUPPORT' || userRole === 'support';
  }

  // Determine if we should use mock data
  isUsingMockData() {
    // Return true if not authenticated or if user doesn't have support role
    return !this.isAuthenticated() || !this.hasSupportRole();
  }

  async getSystemHealth() {
    // If not authenticated or doesn't have support role, return mock data immediately
    if (this.isUsingMockData()) {
      return this.getMockSystemHealth();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/health`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      return this.getMockSystemHealth();
    }
  }

  getMockSystemHealth() {
    return {
      status: "degraded",
      timestamp: new Date().toISOString(),
      services: {
        database: "up",
        redis: "mock",
        api: "up"
      },
      metrics: {
        cpu_usage: 45,
        memory_usage: 62,
        disk_usage: 73,
        active_connections: 15,
        response_time: 150,
        error_rate: 0.5
      }
    };
  }

  async getPerformanceMetrics(timeRange = '24h') {
    if (!this.isAuthenticated()) {
      return this.getMockPerformanceMetrics();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/performance`, {
        params: { time_range: timeRange },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      return this.getMockPerformanceMetrics();
    }
  }

  getMockPerformanceMetrics() {
    return {
      current: {
        response_time: 120,
        request_rate: 15.4,
        error_rate: 0.8
      },
      history: Array(24).fill(0).map((_, i) => ({
        timestamp: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
        response_time: 100 + Math.random() * 50,
        request_rate: 10 + Math.random() * 10,
        error_rate: Math.random() * 2
      }))
    };
  }

  async getErrorLogs(filters = {}) {
    if (!this.isAuthenticated()) {
      return this.getMockErrorLogs();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/errors`, {
        params: filters,
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching error logs:', error);
      return this.getMockErrorLogs();
    }
  }

  getMockErrorLogs() {
    return Array(10).fill(0).map((_, i) => ({
      id: `err-${i}`,
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      severity: ['error', 'warning', 'info'][Math.floor(Math.random() * 3)],
      component: ['api', 'database', 'frontend', 'auth'][Math.floor(Math.random() * 4)],
      message: `Mock error message ${i}`,
      stackTrace: `Error: Something went wrong\n  at function (file.js:${i})\n  at caller (app.js:${i*2})`,
      context: { userId: 'user123', requestId: `req-${i}` }
    }));
  }

  async getActiveAlerts() {
    if (!this.isAuthenticated()) {
      return this.getMockAlerts();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/alerts`, {
        params: { resolved: false },
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching active alerts:', error);
      return this.getMockAlerts();
    }
  }

  getMockAlerts() {
    return Array(3).fill(0).map((_, i) => ({
      id: `alert-${i}`,
      type: ['high_cpu_usage', 'high_error_rate', 'disk_space_low'][i],
      severity: ['critical', 'warning', 'info'][i],
      message: `Mock alert ${i}`,
      timestamp: new Date(Date.now() - i * 1800000).toISOString(),
      resolved: false
    }));
  }

  async dismissAlert(alertId) {
    if (!this.isAuthenticated()) {
      return { success: true, message: 'Alert dismissed (mock)' };
    }

    try {
      const response = await axios.post(`${API_URL}/monitoring/alerts/${alertId}/dismiss`, {}, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error dismissing alert:', error);
      return { success: true, message: 'Alert dismissed (mock)' };
    }
  }

  async getResourceUsage() {
    if (!this.isAuthenticated()) {
      return this.getMockResourceUsage();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/metrics`, {
        headers: this.getAuthHeaders()
      });
      return {
        cpu: response.data.current.cpu_usage,
        memory: response.data.current.memory_usage,
        disk: response.data.current.disk_usage
      };
    } catch (error) {
      console.error('Error fetching resource usage:', error);
      return this.getMockResourceUsage();
    }
  }

  getMockResourceUsage() {
    return {
      cpu: 65,
      memory: 78,
      disk: 52
    };
  }

  async getEndpointPerformance() {
    if (!this.isAuthenticated()) {
      return this.getMockEndpointPerformance();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/endpoints`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching endpoint performance:', error);
      return this.getMockEndpointPerformance();
    }
  }

  getMockEndpointPerformance() {
    return [
      { path: '/api/v1/auth/login', avg_response_time: 120, request_count: 450, error_rate: 0.5, status: 'healthy' },
      { path: '/api/v1/users', avg_response_time: 85, request_count: 320, error_rate: 0.2, status: 'healthy' },
      { path: '/api/v1/courses', avg_response_time: 210, request_count: 180, error_rate: 1.2, status: 'degraded' },
      { path: '/api/v1/assignments', avg_response_time: 310, request_count: 90, error_rate: 3.5, status: 'critical' }
    ];
  }

  async exportLogs(filters = {}) {
    if (!this.isAuthenticated()) {
      return this.getMockExportLogs();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/errors`, {
        params: filters,
        headers: this.getAuthHeaders()
      });
      const exportData = JSON.stringify(response.data, null, 2);
      return new Blob([exportData], { type: 'application/json' });
    } catch (error) {
      console.error('Error exporting logs:', error);
      return this.getMockExportLogs();
    }
  }

  getMockExportLogs() {
    const mockData = JSON.stringify([
      { timestamp: new Date().toISOString(), severity: 'error', message: 'Mock export data' }
    ], null, 2);
    return new Blob([mockData], { type: 'application/json' });
  }

  async resolveError(errorId) {
    if (!this.isAuthenticated()) {
      return { success: true, message: 'Error resolved (mock)' };
    }

    try {
      const response = await axios.post(`${API_URL}/monitoring/errors/${errorId}/resolve`, {}, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error resolving error:', error);
      return { success: true, message: 'Error resolved (mock)' };
    }
  }

  async getSystemMetrics() {
    if (!this.isAuthenticated()) {
      return this.getMockSystemMetrics();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/metrics`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      return this.getMockSystemMetrics();
    }
  }

  getMockSystemMetrics() {
    return {
      current: {
        cpu_usage: 65,
        memory_usage: 78,
        disk_usage: 52,
        active_connections: 12,
        response_time: 130,
        error_rate: 0.7,
        timestamp: new Date().toISOString()
      }
    };
  }

  async getDashboardData() {
    if (!this.isAuthenticated()) {
      return this.getMockDashboardData();
    }

    try {
      const response = await axios.get(`${API_URL}/monitoring/dashboard`, {
        headers: this.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      return this.getMockDashboardData();
    }
  }

  getMockDashboardData() {
    return {
      active_users: 125,
      open_issues: 8,
      system_status: 'healthy',
      avg_response_time: 145,
      recent_errors: [
        { id: 'err-1', timestamp: new Date().toISOString(), severity: 'error', message: 'Database connection timeout' },
        { id: 'err-2', timestamp: new Date(Date.now() - 3600000).toISOString(), severity: 'warning', message: 'High memory usage detected' }
      ]
    };
  }

  // WebSocket connection for real-time updates
  setupWebSocket() {
    if (this.wsConnection) {
      console.log("WebSocket connection already exists");
      return this.wsConnection;
    }
    
    if (!this.isAuthenticated()) {
      console.log("User not authenticated, skipping WebSocket setup");
      return null;
    }
    
    try {
      const token = localStorage.getItem('token');
      // Fix: Use the backend URL instead of relative URL that defaults to frontend server
      // Change from relative path to absolute backend URL
      const wsBaseUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
      const wsUrl = `${wsBaseUrl}/monitoring/ws?token=${token}`;
      
      console.log("Connecting to WebSocket at:", wsUrl);
      
      this.wsConnection = new WebSocket(wsUrl);
      
      this.wsConnection.onopen = () => {
        console.log("WebSocket connection established");
      };
      
      this.wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket message received:", data);
          
          // Handle different types of messages
          switch (data.type) {
            case 'health_update':
              this.handleHealthUpdate(data.data);
              break;
            case 'alert':
              this.handleAlertUpdate(data.data);
              break;
            case 'performance_update':
              this.handlePerformanceUpdate(data.data);
              break;
            default:
              console.log("Unknown WebSocket message type:", data.type);
          }
        } catch (error) {
          console.error("Error processing WebSocket message:", error);
        }
      };
      
      this.wsConnection.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
      
      this.wsConnection.onclose = () => {
        console.log("WebSocket connection closed");
        this.wsConnection = null;
        
        // Attempt to reconnect after a delay
        setTimeout(() => this.setupWebSocket(), 5000);
      };
      
      return this.wsConnection;
    } catch (error) {
      console.error("Error setting up WebSocket:", error);
      return null;
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