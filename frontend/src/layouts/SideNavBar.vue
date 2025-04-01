<template>
  <div class="flex h-[calc(100vh-4rem)]">
    <nav
      class="w-16 hover:w-48 transition-all duration-300 ease-in-out bg-gradient-to-b from-maroon-800 to-maroon-600 flex flex-col p-3 text-white overflow-hidden"
      role="navigation"
      aria-label="Main Navigation"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <!-- Main Navigation -->
      <div class="flex-1 flex flex-col min-h-0">
        <div class="flex-1 flex items-center custom-scrollbar">
          <ul class="w-full space-y-1">
            <li v-for="item in navItems" :key="item.path" class="w-full">
              <router-link
                :to="item.path"
                @mouseenter="isHovered = item.path"
                @mouseleave="isHovered = null"
                class="flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 hover:bg-maroon-700/50"
                :class="{ 'bg-maroon-700': isActive(item.path) }"
                :aria-current="isActive(item.path) ? 'page' : undefined"
              >
                <span
                  class="material-symbols-outlined transition-transform duration-200 text-white"
                  :class="{
                    'text-yellow-400': isActive(item.path),
                    'scale-110': isHovered === item.path,
                  }"
                  aria-hidden="true"
                >
                  {{ item.icon }}
                </span>
                <span
                  class="text-sm font-medium whitespace-nowrap transition-opacity duration-200 text-white"
                  :class="{
                    'opacity-100': navHovered || isHovered === item.path,
                    'opacity-0': !navHovered && isHovered !== item.path,
                    'text-yellow-400': (navHovered || isHovered === item.path) && isActive(item.path),
                    'text-white': (navHovered || isHovered === item.path) && !isActive(item.path),
                  }"
                >
                  {{ item.label }}
                </span>
              </router-link>
            </li>
            <!-- Student Navigation Items -->
            <div v-if="userRole === 'student'" class="space-y-1">
              <router-link
                v-for="link in studentLinks"
                :key="link.to"
                :to="link.to"
                class="flex items-center px-4 py-2 rounded-lg transition-colors"
                :class="[
                  isActive(link.to)
                    ? 'bg-maroon-900 text-white'
                    : 'text-gray-300 hover:bg-maroon-800 hover:text-white',
                ]"
              >
                <span class="material-icons text-lg mr-3">{{ link.icon }}</span>
                {{ link.label }}
              </router-link>
            </div>
          </ul>
        </div>
      </div>

      <!-- Role Switcher (Development Only) -->
      <div v-if="isDevelopment" class="flex-shrink-0 w-full pt-4 border-t border-maroon-700/50">
        <button
          @click="toggleRoleSwitcher"
          class="w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 hover:bg-maroon-700/50 text-white"
          :class="{ 'bg-maroon-700': showRoleSwitcher }"
        >
          <span class="material-symbols-outlined text-yellow-400/90">admin_panel_settings</span>
          <span
            class="text-sm font-medium whitespace-nowrap transition-opacity duration-200 text-white"
            :class="{
              'opacity-100': navHovered,
              'opacity-0': !navHovered,
            }"
          >
            Switch Role
          </span>
        </button>
        
        <!-- Role Options -->
        <div 
          v-show="showRoleSwitcher" 
          class="mt-2 space-y-1 max-h-[120px] custom-scrollbar"
        >
          <button
            v-for="role in roles"
            :key="role"
            @click="switchRole(role)"
            class="w-full flex items-center space-x-3 p-2 rounded-lg transition-all duration-200 hover:bg-maroon-700/50 text-white"
            :class="{
              'bg-maroon-700 text-yellow-400': currentRole === role,
            }"
          >
            <span class="material-symbols-outlined text-sm text-white">
              {{ getRoleIcon(role) }}
            </span>
            <span
              class="text-sm whitespace-nowrap transition-opacity duration-200 text-white"
              :class="{
                'opacity-100': navHovered,
                'opacity-0': !navHovered,
                'text-yellow-400': currentRole === role,
              }"
            >
              {{ role.toLowerCase() }}
            </span>
          </button>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  studentDashboardUrls,
  facultyDashboardUrls,
  supportDashboardUrls,
} from '@/AppConstants/sideNavBarUrls'
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'
import { LAYOUT_CONFIG, ICON_CONFIG, ROLE_ICONS } from '@/config/layout.config'

// Development mode check using Vite environment variable
const isDevelopment = computed(() => import.meta.env.VITE_NODE_ENV === 'development')

// Get the current route for active link detection
const route = useRoute()
const router = useRouter()

// State management
const isHovered = ref(null)
const navHovered = ref(false)
const showRoleSwitcher = ref(false)
let collapseTimeout = null

// Mouse event handlers with auto-collapse
const handleMouseEnter = () => {
  if (collapseTimeout) {
    clearTimeout(collapseTimeout)
    collapseTimeout = null
  }
  navHovered.value = true
}

const handleMouseLeave = () => {
  collapseTimeout = setTimeout(() => {
    navHovered.value = false
    showRoleSwitcher.value = false
  }, 300) // Match transition duration
}

// Helper function to check if a nav item is active
const isActive = (path) => route.path === path

// Get User Store
const userStore = useAuthStore()
const userRole = computed(() => userStore.userRole)
const currentRole = computed(() => userStore.userRole)
const roles = Object.values(ROLE)

const getRoleIcon = (role) => {
  return ROLE_ICONS[role] || ROLE_ICONS.DEFAULT
}

// Navigation items based on role
const navItems = computed(() => {
  const roleUrls = {
    [ROLE.STUDENT]: studentDashboardUrls,
    [ROLE.FACULTY]: facultyDashboardUrls,
    [ROLE.SUPPORT]: supportDashboardUrls
  }
  return roleUrls[userRole.value] || []
})

const toggleRoleSwitcher = () => {
  showRoleSwitcher.value = !showRoleSwitcher.value
}

const switchRole = (role) => {
  userStore.switchRole(role)
  showRoleSwitcher.value = false
}

// Cleanup on component unmount
onUnmounted(() => {
  if (collapseTimeout) {
    clearTimeout(collapseTimeout)
  }
})

// New student links
const studentLinks = [
  { to: '/user/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { to: '/user/courses', label: 'Courses', icon: 'school' },
  { to: '/user/notifications', label: 'Notifications', icon: 'notifications' },
  { to: '/user/profile', label: 'Profile', icon: 'person' },
]

const logout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<style>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' v-bind('ICON_CONFIG.VARIATION_SETTINGS.FILL'),
    'wght' v-bind('ICON_CONFIG.VARIATION_SETTINGS.WEIGHT'),
    'GRAD' v-bind('ICON_CONFIG.VARIATION_SETTINGS.GRADE'),
    'opsz' v-bind('ICON_CONFIG.VARIATION_SETTINGS.OPTICAL_SIZE');
  font-size: v-bind('ICON_CONFIG.DEFAULT_SIZE');
}

/* Pulse animation for icons on hover */
@keyframes iconPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(v-bind('LAYOUT_CONFIG.ANIMATIONS.HOVER_SCALE'));
  }
  100% {
    transform: scale(1);
  }
}

.material-symbols-outlined:hover {
  animation: iconPulse v-bind('LAYOUT_CONFIG.SIDEBAR.TRANSITION_DURATION') v-bind('LAYOUT_CONFIG.ANIMATIONS.TRANSITION_TIMING');
}

/* Custom scrollbar styles */
.custom-scrollbar {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}
</style>
