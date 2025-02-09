<template>
  <header class="bg-white shadow-sm fixed w-full top-0 z-50">
    <div class="container mx-auto px-4 py-3 sm:py-4 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <div
          class="w-8 h-8 sm:w-10 sm:h-10 bg-maroon-600 rounded-lg flex items-center justify-center"
        >
          <span class="material-icons text-white text-base sm:text-xl">school</span>
        </div>
        <router-link
          :to="dashboardUrl"
          class="font-bold text-lg sm:text-xl text-maroon-600 hover:text-maroon-700 transition-colors duration-200"
        >
          Academic Guide
        </router-link>
      </div>

      <div class="relative">
        <button @click="toggleMenu" class="lg:hidden text-maroon-600 focus:outline-none p-2">
          <span class="material-icons">{{ isMenuOpen ? 'close' : 'menu' }}</span>
        </button>

        <nav
          :class="{ block: isMenuOpen, hidden: !isMenuOpen }"
          class="lg:flex items-center absolute lg:relative right-0 top-full lg:top-auto bg-white lg:bg-transparent shadow-lg lg:shadow-none rounded-lg lg:rounded-none p-4 lg:p-0 mt-2 lg:mt-0 w-48 lg:w-auto"
        >
          <ul class="flex flex-col lg:flex-row space-y-3 lg:space-y-0 lg:space-x-6">
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
          </ul>
        </nav>
      </div>
    </div>

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
  </header>
</template>

<script>
import { ROLE } from '@/AppConstants/globalConstants'
import useAuthStore from '@/stores/useAuthStore'

export default {
  name: 'MainNavbar',
  data() {
    return {
      isMenuOpen: false,
      dashboardUrl: '/',
      showNotifications: false,
      notifications: ['New assignment posted', 'Your grade has been updated'], // Sample notifications
    }
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },
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
  watch: {
    $route() {
      this.isMenuOpen = false
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
