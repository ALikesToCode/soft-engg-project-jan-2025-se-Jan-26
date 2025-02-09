<template>
  <BaseNavbar :home-url="dashboardUrl">
    <template #nav-items>
      <li v-if="isProfilePage">
        <router-link
          to="/user/dashboard"
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200"
          :class="{ 'text-maroon-600 font-semibold': $route.name === 'home' }"
        >
          <span class="material-symbols-outlined text-lg">dashboard</span>
          <span class="hover:underline">Dashboard</span>
        </router-link>
      </li>
      <li v-else>
        <router-link
          to="/user/profile"
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200"
          :class="{ 'text-maroon-600 font-semibold': $route.name === 'home' }"
        >
          <span class="material-symbols-outlined text-lg">account_circle</span>
          <span class="hover:underline">My Profile</span>
        </router-link>
      </li>

      <li class="relative">
        <button
          @click="toggleNotifications"
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200"
        >
          <span class="material-symbols-outlined text-lg">circle_notifications</span>
          <span class="hover:underline">Notification</span>
        </button>
        <!-- Notification Badge -->
        <span
          v-if="notifications.length"
          class="absolute -top-1 -right-2 bg-maroon-600 text-white text-xs font-bold px-2 py-0.5 rounded-full"
        >
          {{ notifications.length }}
        </span>
      </li>

      <li>
        <router-link
          @click="logout"
          to="/logout"
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200"
          :class="{ 'text-maroon-600 font-semibold': $route.name === 'home' }"
        >
          <span class="material-symbols-outlined">logout</span>
          <span class="hover:underline">Logout</span>
        </router-link>
      </li>
    </template>

    <template #additional-content>
      <!-- Notification Modal -->
      <div
        v-if="showNotifications"
        class="fixed inset-0 flex items-center justify-center lg:items-start lg:justify-end lg:p-4 z-50 backdrop-blur-xs bg-black bg-opacity-30"
      >
        <div
          class="bg-white p-6 rounded-lg shadow-lg w-80 lg:w-96 relative lg:absolute lg:top-16 lg:right-5"
        >
          <h2 class="text-lg font-bold mb-3 text-center">Notifications</h2>

          <ul v-if="notifications.length">
            <li
              v-for="(notification, index) in notifications"
              :key="index"
              class="p-3 border-b text-sm"
            >
              {{ notification }}
            </li>
          </ul>
          <p v-else class="text-gray-500 py-4 text-center">No new notifications</p>

          <button
            @click="showNotifications = false"
            class="absolute top-2 right-2 text-white bg-red-600 hover:bg-red-700 px-2.5 py-1 rounded"
          >
            ✖
          </button>
        </div>
      </div>
    </template>
  </BaseNavbar>
</template>

<script>
import { ROLE } from '@/AppConstants/globalConstants'
import useAuthStore from '@/stores/useAuthStore'
import BaseNavbar from './BaseNavbar.vue'

export default {
  name: 'UserNavbar',
  components: {
    BaseNavbar
  },
  data() {
    return {
      showNotifications: false,
      notifications: ['New assignment posted', 'Your grade has been updated'], // Sample notifications
    }
  },
  methods: {
    logout() {
      this.userStore.logout()
      this.$router.push({ path: '/', query: { logout: 'true' } })
    },
    toggleNotifications() {
      this.showNotifications = !this.showNotifications
    },
  },
  computed: {
    userStore() {
      return useAuthStore()
    },
    userRole() {
      return this.userStore.userRole
    },
    dashboardUrl() {
      if (this.userRole === ROLE.STUDENT) {
        return '/user/dashboard'
      } else if (this.userRole === ROLE.FACULTY) {
        return '/faculty/dashboard'
      }
      return '/'
    },
    isProfilePage() {
      return this.$route.meta.isProfilePage
    },
  },
}
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
  font-size: 24px;
}
</style>
