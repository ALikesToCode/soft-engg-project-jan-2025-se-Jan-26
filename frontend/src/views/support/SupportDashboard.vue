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
            <div class="mt-2 text-sm text-green-600">↑ 12% vs last hour</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">Open Issues</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900">{{ openIssues }}</div>
            <div class="mt-2 text-sm text-red-600">↑ 3 new in last hour</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">System Status</div>
            <div class="mt-2 text-3xl font-semibold" :class="systemStatusColor">
              {{ systemStatus }}
            </div>
            <div class="mt-2 text-sm text-gray-500">All systems operational</div>
          </div>
          
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-sm font-medium text-gray-500">Average Response Time</div>
            <div class="mt-2 text-3xl font-semibold text-gray-900">{{ avgResponseTime }}ms</div>
            <div class="mt-2 text-sm text-green-600">↓ 5% vs last hour</div>
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
          
          <div class="space-y-4">
            <div v-for="alert in activeAlerts" :key="alert.id"
                 :class="['p-4 rounded-lg', getAlertClass(alert.severity)]">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold">{{ alert.title }}</h3>
                  <p class="text-sm mt-1">{{ alert.message }}</p>
                  <div class="text-sm text-gray-500 mt-2">
                    {{ formatDate(alert.timestamp) }} · {{ alert.component }}
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import SideNavBar from '../../layouts/SideNavBar.vue';
import SystemHealth from '../../components/support/monitoring/SystemHealth.vue';
import PerformanceMetrics from '../../components/support/monitoring/PerformanceMetrics.vue';
import ErrorReporting from '../../components/support/monitoring/ErrorReporting.vue';

export default {
  name: 'SupportDashboard',
  components: {
    SideNavBar,
    SystemHealth,
    PerformanceMetrics,
    ErrorReporting
  },
  setup() {
    // Quick stats
    const activeUsers = ref(1250);
    const openIssues = ref(8);
    const systemStatus = ref('Healthy');
    const avgResponseTime = ref(120);

    const systemStatusColor = computed(() => {
      const colors = {
        'Healthy': 'text-green-600',
        'Degraded': 'text-yellow-600',
        'Critical': 'text-red-600'
      };
      return colors[systemStatus.value] || 'text-gray-600';
    });

    // Active alerts
    const activeAlerts = ref([
      {
        id: 1,
        severity: 'critical',
        title: 'High Memory Usage',
        message: 'Server memory usage exceeds 90%',
        timestamp: new Date().getTime() - 1800000,
        component: 'Database Server'
      },
      {
        id: 2,
        severity: 'warning',
        title: 'API Response Time',
        message: 'Average response time increased by 25%',
        timestamp: new Date().getTime() - 3600000,
        component: 'API Gateway'
      }
    ]);

    const getAlertClass = (severity) => {
      const classes = {
        critical: 'bg-red-50 text-red-800 border border-red-200',
        warning: 'bg-yellow-50 text-yellow-800 border border-yellow-200',
        info: 'bg-blue-50 text-blue-800 border border-blue-200'
      };
      return classes[severity] || 'bg-gray-50 text-gray-800 border border-gray-200';
    };

    const formatDate = (timestamp) => {
      return new Date(timestamp).toLocaleString();
    };

    const refreshAlerts = async () => {
      // Implement alert refresh logic
      console.log('Refreshing alerts');
    };

    const dismissAlert = (alertId) => {
      activeAlerts.value = activeAlerts.value.filter(alert => alert.id !== alertId);
    };

    return {
      // Quick stats
      activeUsers,
      openIssues,
      systemStatus,
      systemStatusColor,
      avgResponseTime,
      
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
