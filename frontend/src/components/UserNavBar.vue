<template>
  <BaseNavbar :home-url="dashboardUrl">
    <template #nav-items>
      <li v-if="isProfilePage">
        <router-link
          :to="dashboardUrl"
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200"
          :class="{ 'text-maroon-600 font-semibold': $route.name === 'home' }"
        >
          <span class="material-symbols-outlined text-lg">dashboard</span>
          <span class="hover:underline">Dashboard</span>
        </router-link>
      </li>
      <li v-else>
        <router-link
          :to="profilePageUrl"
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
          class="flex items-center space-x-2 text-gray-700 hover:text-maroon-600 font-medium py-1 px-2 rounded-md transition-colors duration-200 relative"
          :class="{ 'text-maroon-600': showNotifications }"
        >
          <span class="material-symbols-outlined text-lg">
            {{ unreadNotifications.length ? 'notifications_active' : 'notifications' }}
          </span>
          <span class="hover:underline">Notifications</span>
          <!-- Notification Badge -->
          <span
            v-if="unreadNotifications.length"
            class="absolute -top-1 -right-1 bg-maroon-600 text-white text-xs font-bold px-2 py-0.5 rounded-full min-w-[20px] text-center"
          >
            {{ unreadNotifications.length > 99 ? '99+' : unreadNotifications.length }}
          </span>
        </button>
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
      <!-- Backdrop -->
      <div
        v-if="showNotifications"
        class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
        @click="showNotifications = false"
      ></div>

      <!-- Notification Panel -->
      <NotificationPanel
        v-if="showNotifications"
        :is-open="showNotifications"
        @close="showNotifications = false"
        @update:unread-count="updateUnreadCount"
      />
    </template>
  </BaseNavbar>
</template>

<script>
import { ROLE } from '@/AppConstants/globalConstants'
import useAuthStore from '@/stores/useAuthStore'
import BaseNavbar from './BaseNavbar.vue'
import rolePaths from '@/AppConstants/rolePaths'
import NotificationPanel from './NotificationPanel.vue'

export default {
  name: 'UserNavbar',
  components: {
    BaseNavbar,
    NotificationPanel,
  },
  data() {
    return {
      showNotifications: false,
      unreadNotifications: [], // This will be populated from your notification store/API
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
    updateUnreadCount(count) {
      // Update the unread notifications count
      // This would typically be handled by your notification store
      this.unreadNotifications = new Array(count)
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
      return rolePaths[this.userRole].dashboard
    },
    profilePageUrl() {
      return rolePaths[this.userRole].profile
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
