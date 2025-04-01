<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800">System Health</h2>
    
    <div class="mb-2">
      <SupportRoleIndicator />
      <MockDataBanner />
    </div>
    
    <!-- System Uptime -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-green-50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold text-gray-700 mb-2">System Uptime</h3>
        <div class="text-3xl font-bold text-green-600">{{ formatUptime }}</div>
      </div>
      
      <div class="bg-blue-50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Response Time</h3>
        <div class="text-3xl font-bold text-blue-600">{{ avgResponseTime }}ms</div>
      </div>
      
      <div :class="['p-4 rounded-lg', serverLoadClass]">
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Server Load</h3>
        <div class="text-3xl font-bold" :class="serverLoadTextClass">{{ serverLoad }}%</div>
      </div>
    </div>

    <!-- Performance Graph -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">Performance Metrics</h3>
      <div class="h-64 bg-gray-50 rounded-lg p-4">
        <canvas ref="performanceChart"></canvas>
      </div>
    </div>

    <!-- Status Indicators -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="(status, name) in services" :key="name"
           class="p-4 rounded-lg border"
           :class="getServiceClass(status)">
        <div class="flex items-center space-x-2">
          <div :class="['w-3 h-3 rounded-full', 
                      status === 'up' ? 'bg-green-500' :
                      status === 'down' ? 'bg-red-500' : 'bg-yellow-500']"></div>
          <span class="font-medium text-gray-700">{{ formatServiceName(name) }}</span>
        </div>
        <div class="text-sm text-gray-500 mt-1">{{ getStatusMessage(status) }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'chart.js/auto';
import monitoringService from '../../../services/monitoring.service';
import SupportRoleIndicator from './SupportRoleIndicator.vue';
import MockDataBanner from './MockDataBanner.vue';

export default {
  name: 'SystemHealth',
  components: {
    SupportRoleIndicator,
    MockDataBanner
  },
  setup() {
    const performanceChart = ref(null);
    const chartInstance = ref(null);
    const uptime = ref(0);
    const avgResponseTime = ref(0);
    const serverLoad = ref(0);
    const services = ref({});
    const performanceData = ref({
      labels: [],
      responseTime: []
    });

    // Format uptime value from seconds to days, hours, minutes
    const formatUptime = computed(() => {
      const days = Math.floor(uptime.value / 86400);
      const hours = Math.floor((uptime.value % 86400) / 3600);
      const minutes = Math.floor((uptime.value % 3600) / 60);
      return `${days}d ${hours}h ${minutes}m`;
    });

    const serverLoadClass = computed(() => {
      if (serverLoad.value < 70) return 'bg-green-50';
      if (serverLoad.value < 90) return 'bg-yellow-50';
      return 'bg-red-50';
    });

    const serverLoadTextClass = computed(() => {
      if (serverLoad.value < 70) return 'text-green-600';
      if (serverLoad.value < 90) return 'text-yellow-600';
      return 'text-red-600';
    });

    const formatServiceName = (name) => {
      // Convert service name to title case with spaces
      return name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
    };

    const getStatusMessage = (status) => {
      if (status === 'up') return 'Running normally';
      if (status === 'down') return 'Service unavailable';
      if (status.includes('mock')) return 'Running in mock mode';
      if (status === 'degraded') return 'Performance issues';
      return 'Status unknown';
    };

    const getServiceClass = (status) => {
      if (status === 'up') return 'bg-green-50 border-green-200';
      if (status === 'down') return 'bg-red-50 border-red-200';
      if (status.includes('mock')) return 'bg-blue-50 border-blue-200';
      return 'bg-yellow-50 border-yellow-200';
    };

    const initChart = () => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
      }
      
      const ctx = performanceChart.value.getContext('2d');
      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: performanceData.value.labels,
          datasets: [{
            label: 'Response Time (ms)',
            data: performanceData.value.responseTime,
            borderColor: 'rgb(59, 130, 246)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    };

    const updateChart = () => {
      if (chartInstance.value) {
        chartInstance.value.data.labels = performanceData.value.labels;
        chartInstance.value.data.datasets[0].data = performanceData.value.responseTime;
        chartInstance.value.update();
      }
    };

    const fetchSystemHealth = async () => {
      try {
        const healthData = await monitoringService.getSystemHealth();
        
        if (healthData.uptime) {
          uptime.value = healthData.uptime;
        }
        
        if (healthData.services) {
          services.value = healthData.services;
        }
        
        if (healthData.metrics && healthData.metrics.response_time) {
          avgResponseTime.value = Math.round(healthData.metrics.response_time);
        }
        
        if (healthData.metrics && healthData.metrics.cpu_usage) {
          serverLoad.value = Math.round(healthData.metrics.cpu_usage);
        }
      } catch (error) {
        console.error('Error fetching system health:', error);
      }
    };

    const fetchPerformanceData = async () => {
      try {
        const metricsData = await monitoringService.getPerformanceMetrics('1h');
        
        if (metricsData && metricsData.history && metricsData.history.length > 0) {
          // Format data for chart
          const labels = [];
          const responseTime = [];
          
          metricsData.history.forEach(point => {
            const date = new Date(point.timestamp);
            labels.push(date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}));
            responseTime.push(point.response_time);
          });
          
          performanceData.value = {
            labels,
            responseTime
          };
          
          updateChart();
        }
      } catch (error) {
        console.error('Error fetching performance data:', error);
      }
    };

    onMounted(async () => {
      await fetchSystemHealth();
      await fetchPerformanceData();
      initChart();
      
      // Set up polling for updates
      const healthInterval = setInterval(fetchSystemHealth, 60000);
      const performanceInterval = setInterval(fetchPerformanceData, 300000);
      
      // Clean up on unmount
      return () => {
        clearInterval(healthInterval);
        clearInterval(performanceInterval);
        if (chartInstance.value) {
          chartInstance.value.destroy();
        }
      };
    });

    watch([performanceData], () => {
      updateChart();
    });

    return {
      performanceChart,
      formatUptime,
      avgResponseTime,
      serverLoad,
      serverLoadClass,
      serverLoadTextClass,
      services,
      formatServiceName,
      getStatusMessage,
      getServiceClass
    };
  }
};
</script> 