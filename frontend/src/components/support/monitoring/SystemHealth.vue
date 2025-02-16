<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800">System Health</h2>
    
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
        <!-- Placeholder for chart component -->
        <canvas ref="performanceChart"></canvas>
      </div>
    </div>

    <!-- Status Indicators -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="service in services" :key="service.name"
           class="p-4 rounded-lg border"
           :class="{'bg-green-50 border-green-200': service.status === 'healthy',
                   'bg-red-50 border-red-200': service.status === 'down',
                   'bg-yellow-50 border-yellow-200': service.status === 'degraded'}">
        <div class="flex items-center space-x-2">
          <div :class="['w-3 h-3 rounded-full', 
                      service.status === 'healthy' ? 'bg-green-500' :
                      service.status === 'down' ? 'bg-red-500' : 'bg-yellow-500']"></div>
          <span class="font-medium text-gray-700">{{ service.name }}</span>
        </div>
        <div class="text-sm text-gray-500 mt-1">{{ service.message }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'SystemHealth',
  setup() {
    const performanceChart = ref(null);
    const uptime = ref(345600); // Example: 4 days in seconds
    const avgResponseTime = ref(120);
    const serverLoad = ref(65);
    const services = ref([
      { name: 'API Server', status: 'healthy', message: 'Running normally' },
      { name: 'Database', status: 'healthy', message: 'Connected' },
      { name: 'Cache', status: 'degraded', message: 'High memory usage' },
      { name: 'File Storage', status: 'healthy', message: 'Available' }
    ]);

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

    onMounted(() => {
      // Initialize performance chart
      const ctx = performanceChart.value.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['12:00', '12:05', '12:10', '12:15', '12:20', '12:25', '12:30'],
          datasets: [{
            label: 'Response Time (ms)',
            data: [100, 120, 115, 130, 125, 135, 120],
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
    });

    return {
      performanceChart,
      formatUptime,
      avgResponseTime,
      serverLoad,
      serverLoadClass,
      serverLoadTextClass,
      services
    };
  }
};
</script> 