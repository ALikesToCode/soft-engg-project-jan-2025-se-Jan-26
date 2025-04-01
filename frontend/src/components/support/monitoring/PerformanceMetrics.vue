<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800">Performance Metrics</h2>
    
    <div class="mb-2">
      <SupportRoleIndicator />
      <MockDataBanner />
    </div>
    
    <div class="flex justify-between items-center mb-6">
      <div class="flex space-x-4">
        <select v-model="timeRange" class="rounded border-gray-300">
          <option value="1h">Last Hour</option>
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
        <button @click="refreshData" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Refresh
        </button>
      </div>
    </div>

    <!-- API Performance -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">API Performance</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
        <div class="bg-white p-4 rounded-lg border border-gray-200">
          <div class="text-sm font-medium text-gray-500">Average Response Time</div>
          <div class="mt-1 text-2xl font-semibold text-gray-900">{{ metrics.avgResponseTime }}ms</div>
          <div class="mt-1 text-sm text-gray-500">
            <span :class="responseTimeTrend.color">
              {{ responseTimeTrend.arrow }} {{ responseTimeTrend.value }}%
            </span>
            vs previous period
          </div>
        </div>
        
        <div class="bg-white p-4 rounded-lg border border-gray-200">
          <div class="text-sm font-medium text-gray-500">Request Rate</div>
          <div class="mt-1 text-2xl font-semibold text-gray-900">{{ metrics.requestRate }}/sec</div>
          <div class="mt-1 text-sm text-gray-500">
            <span :class="requestRateTrend.color">
              {{ requestRateTrend.arrow }} {{ requestRateTrend.value }}%
            </span>
            vs previous period
          </div>
        </div>

        <div class="bg-white p-4 rounded-lg border border-gray-200">
          <div class="text-sm font-medium text-gray-500">Error Rate</div>
          <div class="mt-1 text-2xl font-semibold text-gray-900">{{ metrics.errorRate }}%</div>
          <div class="mt-1 text-sm text-gray-500">
            <span :class="errorRateTrend.color">
              {{ errorRateTrend.arrow }} {{ errorRateTrend.value }}%
            </span>
            vs previous period
          </div>
        </div>
      </div>
      
      <div class="h-64 bg-white rounded-lg border border-gray-200 p-4">
        <canvas ref="apiChart"></canvas>
      </div>
    </div>

    <!-- Resource Usage -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">Resource Usage</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- CPU Usage -->
        <div class="bg-white p-4 rounded-lg border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="text-sm font-medium text-gray-500">CPU Usage</div>
            <div class="text-lg font-semibold text-gray-900">{{ metrics.cpuUsage }}%</div>
          </div>
          <div class="relative pt-1">
            <div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
              <div :style="{ width: metrics.cpuUsage + '%' }"
                   :class="cpuUsageClass"
                   class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500">
              </div>
            </div>
          </div>
        </div>

        <!-- Memory Usage -->
        <div class="bg-white p-4 rounded-lg border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <div class="text-sm font-medium text-gray-500">Memory Usage</div>
            <div class="text-lg font-semibold text-gray-900">{{ metrics.memoryUsage }}%</div>
          </div>
          <div class="relative pt-1">
            <div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
              <div :style="{ width: metrics.memoryUsage + '%' }"
                   :class="memoryUsageClass"
                   class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Endpoint Performance -->
    <div>
      <h3 class="text-lg font-semibold text-gray-700 mb-4">Endpoint Performance</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Response Time</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Request Count</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Error Rate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="endpoint in endpoints" :key="endpoint.path" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ endpoint.path }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ endpoint.avg_response_time }}ms
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ endpoint.request_count }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ endpoint.error_rate }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(endpoint.status)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ endpoint.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import Chart from 'chart.js/auto';
import monitoringService from '../../../services/monitoring.service';
import MockDataBanner from './MockDataBanner.vue';
import SupportRoleIndicator from './SupportRoleIndicator.vue';

export default {
  name: 'PerformanceMetrics',
  components: {
    MockDataBanner,
    SupportRoleIndicator
  },
  setup() {
    const timeRange = ref('24h');
    const apiChart = ref(null);
    const chartInstance = ref(null);
    
    // Performance data
    const metrics = ref({
      avgResponseTime: 0,
      requestRate: 0,
      errorRate: 0,
      cpuUsage: 0,
      memoryUsage: 0
    });

    const endpoints = ref([]);
    const performanceHistory = ref({
      labels: [],
      responseTime: [],
      requestRate: []
    });

    // Computed properties for trends
    const responseTimeTrend = computed(() => ({
      value: 5,
      arrow: '↑',
      color: 'text-red-500'
    }));

    const requestRateTrend = computed(() => ({
      value: 12,
      arrow: '↑',
      color: 'text-green-500'
    }));

    const errorRateTrend = computed(() => ({
      value: 0.2,
      arrow: '↓',
      color: 'text-green-500'
    }));

    const cpuUsageClass = computed(() => {
      if (metrics.value.cpuUsage < 70) return 'bg-green-600';
      if (metrics.value.cpuUsage < 90) return 'bg-yellow-600';
      return 'bg-red-600';
    });

    const memoryUsageClass = computed(() => {
      if (metrics.value.memoryUsage < 70) return 'bg-green-600';
      if (metrics.value.memoryUsage < 90) return 'bg-yellow-600';
      return 'bg-red-600';
    });

    const getStatusClass = (status) => {
      const classes = {
        healthy: 'bg-green-100 text-green-800',
        degraded: 'bg-yellow-100 text-yellow-800',
        critical: 'bg-red-100 text-red-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    };

    const initChart = () => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
      }
      
      const ctx = apiChart.value.getContext('2d');
      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: performanceHistory.value.labels,
          datasets: [
            {
              label: 'Response Time (ms)',
              data: performanceHistory.value.responseTime,
              borderColor: 'rgb(59, 130, 246)',
              tension: 0.4
            },
            {
              label: 'Request Rate (req/s)',
              data: performanceHistory.value.requestRate,
              borderColor: 'rgb(16, 185, 129)',
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
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
        chartInstance.value.data.labels = performanceHistory.value.labels;
        chartInstance.value.data.datasets[0].data = performanceHistory.value.responseTime;
        chartInstance.value.data.datasets[1].data = performanceHistory.value.requestRate;
        chartInstance.value.update();
      }
    };

    const fetchPerformanceData = async () => {
      try {
        // Fetch performance metrics
        const performanceData = await monitoringService.getPerformanceMetrics(timeRange.value);
        
        if (performanceData && performanceData.current) {
          metrics.value = {
            avgResponseTime: Math.round(performanceData.current.response_time || 0),
            requestRate: performanceData.current.request_rate || 0,
            errorRate: performanceData.current.error_rate || 0,
            // These might come from system metrics
            cpuUsage: 65, // Mock data
            memoryUsage: 78 // Mock data
          };
        }
        
        // Process history data for chart
        if (performanceData && performanceData.history && performanceData.history.length > 0) {
          const labels = [];
          const responseTime = [];
          const requestRate = [];
          
          performanceData.history.forEach(point => {
            const date = new Date(point.timestamp);
            labels.push(date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}));
            responseTime.push(point.response_time);
            requestRate.push(point.request_rate);
          });
          
          performanceHistory.value = {
            labels,
            responseTime,
            requestRate
          };
          
          updateChart();
        }
        
        // Fetch system metrics for resource usage
        const systemMetrics = await monitoringService.getSystemMetrics();
        if (systemMetrics && systemMetrics.current) {
          metrics.value.cpuUsage = Math.round(systemMetrics.current.cpu_usage || 0);
          metrics.value.memoryUsage = Math.round(systemMetrics.current.memory_usage || 0);
        }
        
        // Fetch endpoint performance
        const endpointData = await monitoringService.getEndpointPerformance();
        if (endpointData && endpointData.length > 0) {
          endpoints.value = endpointData;
        }
      } catch (error) {
        console.error('Error fetching performance data:', error);
      }
    };

    const refreshData = async () => {
      await fetchPerformanceData();
    };

    onMounted(async () => {
      await fetchPerformanceData();
      initChart();
      
      // Set up polling for regular updates
      const updateInterval = setInterval(fetchPerformanceData, 60000); // Update every minute
      
      // Clean up on unmount
      return () => {
        clearInterval(updateInterval);
        if (chartInstance.value) {
          chartInstance.value.destroy();
        }
      };
    });

    watch([timeRange], async () => {
      await fetchPerformanceData();
    });

    watch([performanceHistory], () => {
      updateChart();
    });

    return {
      timeRange,
      apiChart,
      metrics,
      endpoints,
      responseTimeTrend,
      requestRateTrend,
      errorRateTrend,
      cpuUsageClass,
      memoryUsageClass,
      getStatusClass,
      refreshData
    };
  }
};
</script> 