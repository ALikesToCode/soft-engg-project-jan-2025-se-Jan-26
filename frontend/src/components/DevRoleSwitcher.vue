<template>
  <div v-if="isDevelopment" class="fixed bottom-4 right-4 z-50">
    <div class="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Development Role Switcher</h3>
      <div class="space-y-2">
        <button
          v-for="role in roles"
          :key="role"
          @click="switchRole(role)"
          class="w-full px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="{
            'bg-maroon-600 text-white': currentRole === role,
            'bg-gray-100 text-gray-700 hover:bg-gray-200': currentRole !== role
          }"
        >
          {{ role.toLowerCase() }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import useAuthStore from '@/stores/useAuthStore'
import { ROLE } from '@/AppConstants/globalConstants'

const authStore = useAuthStore()
const isDevelopment = computed(() => authStore.isDevelopment)
const currentRole = computed(() => authStore.userRole)
const roles = Object.values(ROLE)

const switchRole = (role) => {
  authStore.switchRole(role)
}
</script> 