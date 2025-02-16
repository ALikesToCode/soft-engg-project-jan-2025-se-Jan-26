<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Side Navigation -->
    <SideNavBar />

    <!-- Main Content -->
    <div class="flex-1 overflow-auto">
      <div v-if="!isAuthorized" class="flex items-center justify-center h-full">
        <div class="text-center">
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Unauthorized Access</h2>
          <p class="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>

      <div v-else class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
          <!-- Header -->
          <div class="mb-8">
            <h1 class="text-2xl font-semibold text-gray-900">System Settings</h1>
            <p class="mt-2 text-sm text-gray-600">
              Manage global system configurations and integrations
            </p>
          </div>

          <!-- Settings Sections -->
          <div class="space-y-6">
            <!-- Authentication Settings -->
            <div class="bg-white shadow rounded-lg">
              <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 mb-4">Authentication Settings</h2>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">JWT Token Expiry (hours)</label>
                    <input
                      type="number"
                      v-model="settings.auth.jwtExpiry"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">OAuth Provider</label>
                    <select
                      v-model="settings.auth.oauthProvider"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      <option value="google">Google</option>
                      <option value="microsoft">Microsoft</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                  <div>
                    <label class="flex items-center">
                      <input
                        type="checkbox"
                        v-model="settings.auth.mfaEnabled"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                      <span class="ml-2 text-sm text-gray-600">Enable Multi-Factor Authentication</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Notification Settings -->
            <div class="bg-white shadow rounded-lg">
              <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 mb-4">Notification Settings</h2>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Default Email Frequency</label>
                    <select
                      v-model="settings.notifications.emailFrequency"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    >
                      <option value="immediate">Immediate</option>
                      <option value="daily">Daily Digest</option>
                      <option value="weekly">Weekly Digest</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">SMTP Server</label>
                    <input
                      type="text"
                      v-model="settings.notifications.smtpServer"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- API Settings -->
            <div class="bg-white shadow rounded-lg">
              <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 mb-4">API Settings</h2>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Rate Limit (requests/minute)</label>
                    <input
                      type="number"
                      v-model="settings.api.rateLimit"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Data Retention Period (days)</label>
                    <input
                      type="number"
                      v-model="settings.api.dataRetentionDays"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Integrations -->
            <div class="bg-white shadow rounded-lg">
              <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                  <h2 class="text-lg font-medium text-gray-900">External Integrations</h2>
                  <button
                    @click="openIntegrationModal"
                    class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Add Integration
                  </button>
                </div>
                
                <div class="space-y-4">
                  <div v-for="integration in settings.integrations" :key="integration.id" 
                       class="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 class="text-sm font-medium text-gray-900">{{ integration.name }}</h3>
                      <p class="text-sm text-gray-500">{{ integration.type }}</p>
                    </div>
                    <div class="flex items-center space-x-4">
                      <span :class="[
                        integration.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                      ]">
                        {{ integration.status }}
                      </span>
                      <button
                        @click="editIntegration(integration)"
                        class="text-gray-400 hover:text-gray-500"
                      >
                        <span class="sr-only">Edit</span>
                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Save Changes -->
            <div class="flex justify-end space-x-4">
              <button
                @click="resetSettings"
                class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Reset Changes
              </button>
              <button
                @click="saveSettings"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Integration Modal -->
    <div v-if="showIntegrationModal && isAuthorized" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-lg w-full p-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-lg font-medium text-gray-900">
            {{ editingIntegration.id ? 'Edit Integration' : 'Add Integration' }}
          </h2>
          <button @click="closeIntegrationModal" class="text-gray-400 hover:text-gray-500">
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveIntegration" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Integration Name</label>
            <input
              type="text"
              v-model="editingIntegration.name"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Type</label>
            <select
              v-model="editingIntegration.type"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="lms">Learning Management System</option>
              <option value="payment">Payment Gateway</option>
              <option value="analytics">Analytics Service</option>
              <option value="ai">AI Service</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">API Endpoint</label>
            <input
              type="url"
              v-model="editingIntegration.endpoint"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">API Key</label>
            <input
              type="password"
              v-model="editingIntegration.apiKey"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>

          <div>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="editingIntegration.status"
                :true-value="'active'"
                :false-value="'inactive'"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-600">Active</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="closeIntegrationModal"
              class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {{ editingIntegration.id ? 'Update' : 'Add' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import SideNavBar from '@/layouts/SideNavBar.vue'
import useAuthStore from '@/stores/useAuthStore'
import { useSystemSettingsStore } from '@/stores/systemSettingsStore'

export default {
  name: 'SystemSettings',
  components: {
    SideNavBar
  },
  setup() {
    const toast = useToast()
    const router = useRouter()
    const authStore = useAuthStore()
    const systemSettingsStore = useSystemSettingsStore()

    // Check if user has admin access, allow in development mode
    const isAuthorized = computed(() => {
      // Always allow access in development mode
      if (import.meta.env.DEV) {
        return true
      }
      return authStore.userRole === 'support'
    })

    // Only redirect in production
    if (!isAuthorized.value && !import.meta.env.DEV) {
      toast.error('Unauthorized access')
      router.push('/support/dashboard')
    }

    const settings = ref({
      auth: {
        jwtExpiry: 24,
        oauthProvider: 'google',
        mfaEnabled: false
      },
      notifications: {
        emailFrequency: 'immediate',
        smtpServer: 'smtp.example.com'
      },
      api: {
        rateLimit: 100,
        dataRetentionDays: 30
      },
      integrations: []
    })

    const showIntegrationModal = ref(false)
    const editingIntegration = ref({
      name: '',
      type: '',
      endpoint: '',
      apiKey: '',
      status: 'inactive'
    })

    // Load initial settings
    onMounted(async () => {
      if (isAuthorized.value) {
        try {
          const currentSettings = await systemSettingsStore.getSettings()
          settings.value = { ...settings.value, ...currentSettings }
        } catch (error) {
          toast.error('Failed to load settings')
        }
      }
    })

    // Integration management
    function openIntegrationModal() {
      editingIntegration.value = {
        name: '',
        type: '',
        endpoint: '',
        apiKey: '',
        status: 'inactive'
      }
      showIntegrationModal.value = true
    }

    function editIntegration(integration) {
      editingIntegration.value = { ...integration }
      showIntegrationModal.value = true
    }

    function closeIntegrationModal() {
      if (confirm('Are you sure you want to close? Any unsaved changes will be lost.')) {
        showIntegrationModal.value = false
        editingIntegration.value = {
          name: '',
          type: '',
          endpoint: '',
          apiKey: '',
          status: 'inactive'
        }
      }
    }

    async function saveIntegration() {
      if (!isAuthorized.value) return

      try {
        if (editingIntegration.value.id) {
          await systemSettingsStore.updateIntegration(editingIntegration.value)
          toast.success('Integration updated successfully')
        } else {
          await systemSettingsStore.addIntegration(editingIntegration.value)
          toast.success('Integration added successfully')
        }
        showIntegrationModal.value = false
        // Refresh settings
        const currentSettings = await systemSettingsStore.getSettings()
        settings.value = { ...settings.value, ...currentSettings }
      } catch (error) {
        toast.error(error.message || 'Failed to save integration')
      }
    }

    // Settings management
    async function saveSettings() {
      if (!isAuthorized.value) return

      try {
        await systemSettingsStore.updateSettings(settings.value)
        toast.success('Settings saved successfully')
      } catch (error) {
        toast.error('Failed to save settings')
      }
    }

    async function resetSettings() {
      if (!isAuthorized.value) return

      if (confirm('Are you sure you want to reset all changes?')) {
        try {
          const currentSettings = await systemSettingsStore.getSettings()
          settings.value = { ...settings.value, ...currentSettings }
          toast.success('Settings reset successfully')
        } catch (error) {
          toast.error('Failed to reset settings')
        }
      }
    }

    return {
      settings,
      showIntegrationModal,
      editingIntegration,
      openIntegrationModal,
      editIntegration,
      closeIntegrationModal,
      saveIntegration,
      saveSettings,
      resetSettings,
      isAuthorized
    }
  }
}
</script> 