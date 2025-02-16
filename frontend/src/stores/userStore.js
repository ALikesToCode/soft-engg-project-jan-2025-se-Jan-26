import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Mock data for development
  const mockUsers = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john.doe@example.com',
      role: 'student',
      status: 'active',
      lastActive: '2024-01-25T10:30:00Z',
      avatar: null
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      role: 'faculty',
      status: 'active',
      lastActive: '2024-01-25T11:45:00Z',
      avatar: null
    },
    {
      id: 3,
      name: 'Mike Johnson',
      email: 'mike.johnson@example.com',
      role: 'support',
      status: 'active',
      lastActive: '2024-01-25T09:15:00Z',
      avatar: null
    },
    {
      id: 4,
      name: 'Sarah Wilson',
      email: 'sarah.wilson@example.com',
      role: 'student',
      status: 'inactive',
      lastActive: '2024-01-24T16:20:00Z',
      avatar: null
    },
    {
      id: 5,
      name: 'Robert Brown',
      email: 'robert.brown@example.com',
      role: 'faculty',
      status: 'pending',
      lastActive: '2024-01-25T08:00:00Z',
      avatar: null
    }
  ]

  // Actions
  async function fetchUsers() {
    try {
      loading.value = true
      if (import.meta.env.DEV) {
        users.value = mockUsers
        return mockUsers
      }

      const response = await axios.get('/api/v1/users')
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
      if (import.meta.env.DEV) {
        const newUser = {
          id: mockUsers.length + 1,
          ...userData,
          lastActive: new Date().toISOString(),
          avatar: null
        }
        mockUsers.push(newUser)
        users.value = mockUsers
        return newUser
      }

      const response = await axios.post('/api/v1/users', userData)
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
      if (import.meta.env.DEV) {
        const index = mockUsers.findIndex(u => u.id === userId)
        if (index !== -1) {
          mockUsers[index] = { ...mockUsers[index], ...userData }
          users.value = mockUsers
          return mockUsers[index]
        }
        throw new Error('User not found')
      }

      const response = await axios.put(`/api/v1/users/${userId}`, userData)
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
      if (import.meta.env.DEV) {
        const index = mockUsers.findIndex(u => u.id === userId)
        if (index !== -1) {
          mockUsers.splice(index, 1)
          users.value = mockUsers
          return
        }
        throw new Error('User not found')
      }

      await axios.delete(`/api/v1/users/${userId}`)
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
      if (import.meta.env.DEV) {
        return [
          {
            id: 1,
            userId,
            action: 'Login',
            details: 'User logged in successfully',
            timestamp: '2024-01-25T10:30:00Z'
          },
          {
            id: 2,
            userId,
            action: 'Profile Update',
            details: 'User updated their profile information',
            timestamp: '2024-01-24T15:45:00Z'
          }
        ]
      }

      const response = await axios.get(`/api/v1/users/${userId}/audit-log`)
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
    // State
    users,
    loading,
    error,
    // Actions
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    getUserAuditLog,
    clearError
  }
}) 