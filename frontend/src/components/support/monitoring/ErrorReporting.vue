<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800">Error Logs</h2>
    
    <div class="mb-2">
      <SupportRoleIndicator />
      <MockDataBanner />
    </div>
    
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Error Logs</h2>
      <div class="flex space-x-4">
        <button @click="exportLogs" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Export Logs
        </button>
        <button @click="showFilters = !showFilters" class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
          Filters
        </button>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
          <select v-model="filters.severity" class="w-full rounded border-gray-300">
            <option value="">All</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Component</label>
          <select v-model="filters.component" class="w-full rounded border-gray-300">
            <option value="">All</option>
            <option value="api">API</option>
            <option value="database">Database</option>
            <option value="frontend">Frontend</option>
            <option value="auth">Authentication</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Time Range</label>
          <select v-model="filters.timeRange" class="w-full rounded border-gray-300">
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input type="text" v-model="filters.search" placeholder="Search logs..." 
                 class="w-full rounded border-gray-300">
        </div>
      </div>
      <div class="flex justify-end mt-4">
        <button @click="applyFilters" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Apply Filters
        </button>
      </div>
    </div>

    <!-- Error Log Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="error in filteredErrors" :key="error.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(error.timestamp) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="severityClass(error.severity)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ error.severity }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ error.component }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ error.message }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button @click="viewDetails(error)" class="text-blue-600 hover:text-blue-900 mr-3">
                Details
              </button>
              <button @click="resolveError(error.id)" class="text-green-600 hover:text-green-900">
                Resolve
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Error Details Modal -->
    <div v-if="selectedError" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-medium">Error Details</h3>
          <button @click="selectedError = null" class="text-gray-400 hover:text-gray-500">
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <h4 class="text-sm font-medium text-gray-500">Stack Trace</h4>
            <pre class="mt-1 bg-gray-50 p-4 rounded text-sm overflow-x-auto">{{ selectedError.stackTrace }}</pre>
          </div>
          <div>
            <h4 class="text-sm font-medium text-gray-500">Additional Context</h4>
            <pre class="mt-1 bg-gray-50 p-4 rounded text-sm">{{ JSON.stringify(selectedError.context, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import monitoringService from '../../../services/monitoring.service';
import MockDataBanner from './MockDataBanner.vue';
import SupportRoleIndicator from './SupportRoleIndicator.vue';

export default {
  name: 'ErrorReporting',
  components: {
    MockDataBanner,
    SupportRoleIndicator
  },
  setup() {
    const showFilters = ref(false);
    const selectedError = ref(null);
    const errors = ref([]);
    const filters = ref({
      severity: '',
      component: '',
      timeRange: '24h',
      search: ''
    });

    const filteredErrors = computed(() => {
      return errors.value.filter(error => {
        if (filters.value.severity && error.severity !== filters.value.severity) return false;
        if (filters.value.component && error.component !== filters.value.component) return false;
        if (filters.value.search) {
          const searchLower = filters.value.search.toLowerCase();
          return error.message.toLowerCase().includes(searchLower) ||
                 error.component.toLowerCase().includes(searchLower);
        }
        return true;
      });
    });

    const formatDate = (timestamp) => {
      if (typeof timestamp === 'string') {
        return new Date(timestamp).toLocaleString();
      }
      return new Date(timestamp).toLocaleString();
    };

    const severityClass = (severity) => {
      const classes = {
        error: 'bg-red-100 text-red-800',
        warning: 'bg-yellow-100 text-yellow-800',
        info: 'bg-blue-100 text-blue-800'
      };
      return classes[severity] || 'bg-gray-100 text-gray-800';
    };

    const fetchErrors = async () => {
      try {
        // Convert timeRange to start/end time if necessary
        const params = { ...filters.value };
        delete params.search; // Remove search from API params
        
        const errorLogs = await monitoringService.getErrorLogs(params);
        errors.value = errorLogs || [];
      } catch (error) {
        console.error('Error fetching error logs:', error);
      }
    };

    const applyFilters = async () => {
      await fetchErrors();
    };

    const viewDetails = (error) => {
      selectedError.value = error;
    };

    const resolveError = async (errorId) => {
      try {
        await monitoringService.resolveError(errorId);
        errors.value = errors.value.filter(error => error.id !== errorId);
      } catch (error) {
        console.error('Error resolving error:', error);
      }
    };

    const exportLogs = () => {
      try {
        // Implement log export logic through service
        monitoringService.exportLogs(filters.value).then(blob => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'error-logs.json';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        });
      } catch (error) {
        console.error('Error exporting logs:', error);
      }
    };

    onMounted(async () => {
      await fetchErrors();
      
      // Set up polling for regular updates
      const updateInterval = setInterval(fetchErrors, 60000); // Update every minute
      
      // Clean up on unmount
      return () => {
        clearInterval(updateInterval);
      };
    });

    return {
      showFilters,
      filters,
      filteredErrors,
      selectedError,
      formatDate,
      severityClass,
      viewDetails,
      resolveError,
      exportLogs,
      applyFilters
    };
  }
};
</script> 