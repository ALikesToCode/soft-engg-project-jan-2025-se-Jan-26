<template>
  <div class="flex h-screen">
    <nav 
      class="w-16 hover:w-48 transition-all duration-300 ease-in-out bg-gradient-to-b from-maroon-800 to-maroon-600 flex flex-col justify-center items-start p-3 text-white overflow-hidden"
      role="navigation"
      aria-label="Main Navigation"
      @mouseenter="navHovered = true"
      @mouseleave="navHovered = false"
    >
      <ul class="w-full">
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
              class="material-symbols-outlined transition-transform duration-200"
              :class="{ 
                'text-yellow-400': isActive(item.path),
                'scale-110': isHovered === item.path
              }"
              aria-hidden="true"
            >
              {{ item.icon }}
            </span>
            <span 
              class="text-sm font-medium whitespace-nowrap transition-opacity duration-200"
              :class="{
                'opacity-100': navHovered || isHovered === item.path,
                'opacity-0': !navHovered && isHovered !== item.path,
                'text-yellow-400': (navHovered || isHovered === item.path) && isActive(item.path),
                'text-white': (navHovered || isHovered === item.path) && !isActive(item.path)
              }"
            >
              {{ item.label }}
            </span>
          </router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

// Get the current route for active link detection.
const route = useRoute()

// Tracks which individual nav item is hovered.
const isHovered = ref(null)

// Tracks whether the entire navigation bar is hovered.
const navHovered = ref(false)

// Define the navigation items.
const navItems = [
  {
    path: '/user/dashboard',
    icon: 'dashboard',
    label: 'Dashboard'
  },
  {
    path: '/user/courses', 
    icon: 'auto_stories',
    label: 'Courses'
  },
  {
    path: '/user/course-history',
    icon: 'history', 
    label: 'History'
  }
]

// Helper function to check if a nav item is active.
const isActive = (path) => route.path === path
</script>

<style>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
  font-size: 24px;
}

/* Pulse animation for icons on hover */
@keyframes iconPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.material-symbols-outlined:hover {
  animation: iconPulse 0.3s ease-in-out;
}
</style>
