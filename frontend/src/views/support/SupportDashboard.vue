<template>
  <div class="flex h-screen bg-gray-100">
    <div>
      <SideNavBar />
    </div>
    <div class="flex-1 overflow-auto">
      <div class="p-6">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-gray-900">Technical Support Dashboard</h1>
          <p class="mt-2 text-gray-600">Monitor system health, performance, and manage technical issues</p>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">Active Users</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900">{{ activeUsers }}</div>
            <div class="mt-2 text-sm text-green-600" v-if="userChange > 0">↑ {{ userChange }}% vs last hour</div>
            <div class="mt-2 text-sm text-red-600" v-else-if="userChange < 0">↓ {{ Math.abs(userChange) }}% vs last hour</div>
            <div class="mt-2 text-sm text-gray-600" v-else>No change vs last hour</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">Open Issues</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900">{{ openIssues }}</div>
            <div class="mt-2 text-sm text-red-600" v-if="newIssues > 0">↑ {{ newIssues }} new in last hour</div>
            <div class="mt-2 text-sm text-green-600" v-else>No new issues in last hour</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">System Status</div>
            <div class="mt-2 text-3xl font-semibold" :class="systemStatusColor">
              {{ systemStatus }}
            </div>
            <div class="mt-2 text-sm text-gray-500">{{ systemStatusMessage }}</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">Average Response Time</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900">{{ avgResponseTime }}ms</div>
            <div class="mt-2 text-sm text-green-600" v-if="responseTimeChange < 0">↓ {{ Math.abs(responseTimeChange) }}% vs last hour</div>
            <div class="mt-2 text-sm text-red-600" v-else-if="responseTimeChange > 0">↑ {{ responseTimeChange }}% vs last hour</div>
            <div class="mt-2 text-sm text-gray-600" v-else>No change vs last hour</div>
          </div>
        </div>

        <!-- System Health -->
        <div class="mb-6">
          <SystemHealth />
        </div>

        <!-- Performance Metrics -->
        <div class="mb-6">
          <PerformanceMetrics />
        </div>

        <!-- Error Reporting -->
        <div class="mb-6">
          <ErrorReporting />
        </div>

        <!-- Active Alerts -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold text-gray-800">Active Alerts</h2>
            <button @click="refreshAlerts" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Refresh
            </button>
          </div>
          
          <div class="space-y-4" v-if="activeAlerts.length > 0">
            <div v-for="alert in activeAlerts" :key="alert.id"
                 :class="['p-4 rounded-lg', getAlertClass(alert.severity)]">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold">{{ alert.type }}</h3>
                  <p class="text-sm mt-1">{{ alert.message }}</p>
                  <div class="text-sm text-gray-500 mt-2">
                    {{ formatDate(alert.timestamp) }}
                  </div>
                </div>
                <button @click="dismissAlert(alert.id)" 
                        class="text-gray-400 hover:text-gray-500">
                  <span class="sr-only">Dismiss</span>
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="p-4 text-center text-gray-500">
            No active alerts at this time
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import SideNavBar from '../../layouts/SideNavBar.vue';
import SystemHealth from '../../components/support/monitoring/SystemHealth.vue';
import PerformanceMetrics from '../../components/support/monitoring/PerformanceMetrics.vue';
import ErrorReporting from '../../components/support/monitoring/ErrorReporting.vue';
import monitoringService from '../../services/monitoring.service';

export default {
  name: 'SupportDashboard',
  components: {
    SideNavBar,
    SystemHealth,
    PerformanceMetrics,
    ErrorReporting
  },
  setup() {
    const router = useRouter();
    
    // Quick stats
    const activeUsers = ref(0);
    const userChange = ref(0);
    const openIssues = ref(0);
    const newIssues = ref(0);
    const systemStatus = ref('Loading...');
    const systemStatusMessage = ref('Checking system status...');
    const avgResponseTime = ref(0);
    const responseTimeChange = ref(0);
    
    // Active alerts
    const activeAlerts = ref([]);
    const refreshInterval = ref(null);
    let wsConnection = null;

    const systemStatusColor = computed(() => {
      const colors = {
        'Healthy': 'text-green-600',
        'Degraded': 'text-yellow-600',
        'Critical': 'text-red-600',
        'Loading...': 'text-gray-600'
      };
      return colors[systemStatus.value] || 'text-gray-600';
    });

    const getAlertClass = (severity) => {
      const classes = {
        'critical': 'bg-red-50 text-red-800 border border-red-200',
        'warning': 'bg-yellow-50 text-yellow-800 border border-yellow-200',
        'info': 'bg-blue-50 text-blue-800 border border-blue-200'
      };
      return classes[severity] || 'bg-gray-50 text-gray-800 border border-gray-200';
    };

    const formatDate = (timestamp) => {
      if (typeof timestamp === 'string') {
        return new Date(timestamp).toLocaleString();
      }
      return new Date(timestamp).toLocaleString();
    };

    const fetchDashboardData = async () => {
      try {
        // Fetch system health
        const healthData = await monitoringService.getSystemHealth();
        
        // Determine system status based on health data
        if (healthData.services) {
          const services = Object.values(healthData.services);
          if (services.some(s => s === 'down')) {
            systemStatus.value = 'Critical';
            systemStatusMessage.value = 'Some services are down';
          } else if (services.some(s => s === 'degraded' || s.includes('mock'))) {
            systemStatus.value = 'Degraded';
            systemStatusMessage.value = 'Some services are degraded';
          } else {
            systemStatus.value = 'Healthy';
            systemStatusMessage.value = 'All systems operational';
          }
        }

        // Fetch system metrics
        const metricsData = await monitoringService.getSystemMetrics();
        if (metricsData && metricsData.current) {
          avgResponseTime.value = Math.round(metricsData.current.response_time || 0);
          // Set a random change for this example, in a real app you'd compare with historical data
          responseTimeChange.value = -5; // Example: 5% improvement
        }

        // Fetch active alerts
        const alertsData = await monitoringService.getActiveAlerts();
        activeAlerts.value = alertsData || [];
        
        // Mock data for active users and open issues
        // In a real implementation, these would come from real API endpoints
        activeUsers.value = 1250;
        userChange.value = 12;
        openIssues.value = 8;
        newIssues.value = 3;
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        systemStatus.value = 'Degraded';
        systemStatusMessage.value = 'Error fetching system data';
      }
    };

    const refreshAlerts = async () => {
      try {
        const alertsData = await monitoringService.getActiveAlerts();
        activeAlerts.value = alertsData || [];
      } catch (error) {
        console.error('Error refreshing alerts:', error);
      }
    };

    const dismissAlert = async (alertId) => {
      try {
        await monitoringService.dismissAlert(alertId);
        activeAlerts.value = activeAlerts.value.filter(alert => alert.id !== alertId);
      } catch (error) {
        console.error('Error dismissing alert:', error);
      }
    };

    const setupRealTimeUpdates = () => {
      try {
        wsConnection = monitoringService.setupWebSocket();
        
        // Override the handlers provided by the service
        monitoringService.handleHealthUpdate = (data) => {
          systemStatus.value = data.status;
          systemStatusMessage.value = data.message || 'System status updated';
        };
        
        monitoringService.handleAlertUpdate = (data) => {
          if (data.action === 'new') {
            activeAlerts.value.unshift(data.alert);
          } else if (data.action === 'resolve') {
            activeAlerts.value = activeAlerts.value.filter(alert => alert.id !== data.alertId);
          }
        };
        
        monitoringService.handlePerformanceUpdate = (data) => {
          if (data.metrics) {
            avgResponseTime.value = Math.round(data.metrics.response_time || 0);
            responseTimeChange.value = data.metrics.response_time_change || 0;
          }
        };
      } catch (error) {
        console.error('Error setting up real-time updates:', error);
      }
    };

    onMounted(() => {
      // Check authentication and role
      if (!monitoringService.isAuthenticated()) {
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        });
        return;
      }
      
      if (!monitoringService.hasSupportRole()) {
        router.push('/dashboard');
        return;
      }
      
      fetchDashboardData();
      
      // Set up refresh interval
      refreshInterval.value = setInterval(() => {
        fetchDashboardData();
      }, 60000); // Refresh every minute
      
      // Set up WebSocket for real-time updates
      setupRealTimeUpdates();
    });

    onUnmounted(() => {
      // Clear interval when component is unmounted
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value);
      }
      
      // Close WebSocket connection
      if (wsConnection) {
        wsConnection.close();
      }
    });

    return {
      // Quick stats
      activeUsers,
      userChange,
      openIssues,
      newIssues,
      systemStatus,
      systemStatusMessage,
      systemStatusColor,
      avgResponseTime,
      responseTimeChange,
      
      // Alerts
      activeAlerts,
      getAlertClass,
      formatDate,
      refreshAlerts,
      dismissAlert
    };
  }
};
</script>
