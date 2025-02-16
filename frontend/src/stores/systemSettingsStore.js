import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useSystemSettingsStore = defineStore('systemSettings', () => {
  // State
  const settings = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Mock data for development
  const mockSettings = {
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
    integrations: [
      {
        id: 1,
        name: 'Canvas LMS',
        type: 'lms',
        endpoint: 'https://canvas.example.com/api',
        status: 'active'
      },
      {
        id: 2,
        name: 'Stripe Payments',
        type: 'payment',
        endpoint: 'https://api.stripe.com/v1',
        status: 'active'
      },
      {
        id: 3,
        name: 'Google Analytics',
        type: 'analytics',
        endpoint: 'https://analytics.google.com/api',
        status: 'inactive'
      }
    ]
  }

  // Actions
  async function getSettings() {
    try {
      loading.value = true
      // For development, return mock data
      if (import.meta.env.DEV) {
        settings.value = mockSettings
        return mockSettings
      }

      const response = await axios.get('/api/v1/admin/settings')
      settings.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(newSettings) {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        settings.value = newSettings
        return newSettings
      }

      const response = await axios.put('/api/v1/admin/settings', newSettings)
      settings.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getIntegrations() {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        return mockSettings.integrations
      }

      const response = await axios.get('/api/v1/admin/integrations')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addIntegration(integration) {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        const newIntegration = {
          id: mockSettings.integrations.length + 1,
          ...integration
        }
        mockSettings.integrations.push(newIntegration)
        return newIntegration
      }

      const response = await axios.post('/api/v1/admin/integrations', integration)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateIntegration(integration) {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        const index = mockSettings.integrations.findIndex(i => i.id === integration.id)
        if (index !== -1) {
          mockSettings.integrations[index] = integration
          return integration
        }
        throw new Error('Integration not found')
      }

      const response = await axios.put(`/api/v1/admin/integrations/${integration.id}`, integration)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteIntegration(integrationId) {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        const index = mockSettings.integrations.findIndex(i => i.id === integrationId)
        if (index !== -1) {
          mockSettings.integrations.splice(index, 1)
          return
        }
        throw new Error('Integration not found')
      }

      await axios.delete(`/api/v1/admin/integrations/${integrationId}`)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    settings,
    loading,
    error,
    // Actions
    getSettings,
    updateSettings,
    getIntegrations,
    addIntegration,
    updateIntegration,
    deleteIntegration,
    clearError
  }
}) 