import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const API_PREFIX = import.meta.env.VITE_API_PREFIX || ''

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchUsers() {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        return [] // Mock users can be added here if needed
      }
      const response = await axios.get(`${API_URL}${API_PREFIX}/users`)
      users.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createUser(userData) {
    try {
      loading.value = true
      const response = await axios.post(`${API_URL}${API_PREFIX}/users/add`, userData)
      users.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateUser(userId, userData) {
    try {
      loading.value = true
      const response = await axios.put(`${API_URL}${API_PREFIX}/users/${userId}`, userData)
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteUser(userId) {
    try {
      loading.value = true
      await axios.delete(`${API_URL}${API_PREFIX}/users/${userId}`)
      users.value = users.value.filter(u => u.id !== userId)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getUserAuditLog(userId) {
    try {
      loading.value = true
      const response = await axios.get(`${API_URL}${API_PREFIX}/users/${userId}/audit-log`)
      return response.data
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
    users,
    loading,
    error,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    getUserAuditLog,
    clearError
  }
})
