<template>
  <div>
    <div class="flex justify-between items-center bg-white p-4 shadow rounded-lg">
      <div class="flex space-x-4 items-center">
        <router-link v-if="showDashboardBtn" :to=dashboardUrl>
          <button class="bg-red-700 text-white px-3 py-2 rounded hover:bg-red-800 hover:cursor-pointer transition">
            <i class="bi bi-arrow-left pr-1"></i>Dashboard
          </button>
          &nbsp;
        </router-link>
        <input
          type="text"
          placeholder="Search..."
          class="border p-2 rounded-lg w-80 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700"
        />
      </div>
      <div class="flex space-x-8 text-2xl relative">
        <router-link :to="detailsPageUrl" class="hover:text-blue-600">
          👤
        </router-link>
        <span @click="toggleNotifications" class="hover:cursor-pointer hover:text-yellow-600 relative">
          🔔
          <span v-if="notifications.length" class="absolute top-0 right-0 bg-red-600 text-white text-xs px-1 rounded-full">
            {{ notifications.length }}
          </span>
        </span>
        &nbsp;
        <span @click="logout" class="hover:cursor-pointer hover:text-red-600" title="Logout">
          <i class="bi bi-box-arrow-right"></i>
        </span>
      </div>
    </div>

    <!-- Notification Modal -->
    <div v-if="showNotifications" class="fixed inset-0 flex items-center justify-center bg-gradient-to-b from-red-600 to-red-500 bg-opacity-30 z-50 px-2.5 py-1" @click="closeModal">
      <div class="bg-white p-5 rounded-lg shadow-lg w-1/2 relative" @click.stop>
        <h2 class="text-2xl font-bold mb-3 text-center">Notifications</h2>
        
        <ul v-if="notifications.length">
          <li v-for="(notification, index) in notifications" :key="index" class="p-2 border-b">
            {{ notification }}
          </li>
        </ul>
        <p v-else class="text-gray-500 py-12 text-center">No new notifications</p>
        <button @click="showNotifications = false" class="absolute top-2 right-2 text-white bg-red-600 hover:bg-red-700 px-2.5 py-1 rounded">
          <i class="bi bi-x-lg text-2xl"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script> 
import { ROLE } from '../AppConstants/globalConstants.js';
import useAuthStore from '../stores/useAuthStore.js'; 
export default {

  data() {
    return {
      dashboardUrl:null,
      searchQuery: "",
      showNotifications: false,
      notifications: ["New message from Admin", "Reminder: Meeting at 3 PM"],
    };
  },
  computed: {
    userStore() {
      return useAuthStore(); // Pinia store
    },
    userRole() {
      return this.userStore.userRole;
    },
    showDashboardBtn() {
      if (this.userRole === ROLE.STUDENT && this.$route.path != '/user/dashboard') {
        this.dashboardUrl = "/user/dashboard";
        return true;
      }
      else if (this.userRole === ROLE.FACULTY && this.$route.path != '/faculty/dashboard') {
        this.dashboardUrl = "/faculty/dashboard";
        return true;
      }
      return false;
    },
    detailsPageUrl() {
      if (this.userRole === ROLE.FACULTY) {
        return "/faculty/details";
      }
      else if (this.userRole === ROLE.STUDENT) {
        return "/user/details";
      }
      else if (this.userRole === ROLE.SUPPORT) {
        return "/support/details";
      }
    }
  },
  methods: {
    logout() {
      this.$router.push({ path: '/', query: { logout: 'true' } });
    },
    toggleNotifications() {
      this.showNotifications = !this.showNotifications;
    },
    closeModal() {
      this.showNotifications = false;
    },
  },
};
</script>

<style scoped>
</style>
