<template>
  <div class="flex h-screen">
    <div>
      <SideNavBar />
    </div>
    <div class="flex-1 p-6">
      <div class="flex justify-end mb-4">
        <button @click="toggleFilter" class="bg-red-700 text-white px-4 py-2 rounded hover:bg-red-800">
          Filter
        </button>
      </div>

      <!-- Backdrop -->
      <div v-if="showFilter" class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40" @click="showFilter = false"></div>

      <!-- Filter Panel -->
      <div v-if="showFilter" class="fixed top-20 right-10 bg-white p-6 rounded-lg shadow-lg z-50 w-80 text-gray-700">
        <h2 class="text-lg font-semibold mb-4">Filter Logs</h2>
        
        <!-- Status Filter -->
        <label class="block text-gray-700">Status</label>
        <select v-model="filterStatus" class="w-full border p-2 rounded mb-3 text-gray-700">
          <option value="">All</option>
          <option value="Success">Success</option>
          <option value="Failed">Failed</option>
        </select>

        <!-- Status Code Filter -->
        <label class="block text-gray-700">Status Code</label>
        <select v-model="filterStatusCode" class="w-full border p-2 rounded mb-3 text-gray-700">
          <option value="">All</option>
          <option value="200">200</option>
          <option value="201">201</option>
          <option value="400">400</option>
          <option value="500">500</option>
        </select>

        <div class="flex justify-end space-x-2">
          <button @click="applyFilters" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Apply
          </button>
          <button @click="resetFilters" class="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">
            Reset
          </button>
          <button @click="toggleFilter" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
            Close
          </button>
        </div>
      </div>

      <div class="bg-white shadow-lg rounded-lg overflow-hidden">
        <table class="min-w-full border border-gray-300">
          <thead class="bg-red-700 text-white">
            <tr>
              <th class="px-4 py-2 text-left">ID</th>
              <th class="px-4 py-2 text-left">Event Name</th>
              <th class="px-4 py-2 text-left">Status</th>
              <th class="px-4 py-2 text-left">Status Code</th>
              <th class="px-4 py-2 text-left">End Point</th>
              <th class="px-4 py-2 text-left">Date and Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(event, index) in filteredLogs" :key="index" class="border-b hover:bg-gray-100 text-gray-700">
              <td class="px-4 py-2">{{ event.id }}</td>
              <td class="px-4 py-2">{{ event.eventName }}</td>
              <td class="px-4 py-2">
                <span :class="{ 'text-green-600': event.status === 'Success', 'text-red-600': event.status === 'Failed' }">
                  {{ event.status }}
                </span>
              </td>
              <td class="px-4 py-2">{{ event.statusCode }}</td>
              <td class="px-4 py-2">{{ event.endPoint || '—' }}</td>
              <td class="px-4 py-2">{{ event.dateTime || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '../../layouts/SideNavBar.vue';

export default {
  name: 'SupportDashboard',
  components: {
    SideNavBar
  },
  data() {
    return {
      showFilter: false,
      filterStatus: '',
      filterStatusCode: '',
      eventLogs: [
        { id: 123456, eventName: 'Lorem Ipsum', status: 'Success', statusCode: 200, endPoint: '', dateTime: '' },
        { id: 123457, eventName: 'Lorem Ipsum', status: 'Failed', statusCode: 500, endPoint: '', dateTime: '' },
        { id: 123458, eventName: 'Lorem Ipsum', status: 'Success', statusCode: 201, endPoint: '', dateTime: '' },
        { id: 123459, eventName: 'Lorem Ipsum', status: 'Failed', statusCode: 400, endPoint: '', dateTime: '' }
      ]
    };
  },
  computed: {
    filteredLogs() {
      return this.eventLogs.filter(event => {
        const statusMatch = this.filterStatus ? event.status === this.filterStatus : true;
        const statusCodeMatch = this.filterStatusCode ? event.statusCode.toString() === this.filterStatusCode : true;
        return statusMatch && statusCodeMatch;
      });
    }
  },
  methods: {
    toggleFilter() {
      this.showFilter = !this.showFilter;
    },
    applyFilters() {
      this.showFilter = false;
    },
    resetFilters() {
      this.filterStatus = '';
      this.filterStatusCode = '';
    }
  }
};
</script>
