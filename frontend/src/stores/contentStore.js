import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import api from '@/utils/api'

export const useContentStore = defineStore('content', () => {
  // State
  const modules = ref([])
  const currentContent = ref(null)
  const contentHistory = ref([])
  const lastSavedContent = ref(null)

  // Getters
  const getModuleById = computed(() => (id) => {
    return modules.value.find(module => module.id === id)
  })

  const getContentByModule = computed(() => (moduleId) => {
    return modules.value.find(m => m.id === moduleId)?.contents || []
  })

  const hasUnsavedChanges = computed(() => {
    return JSON.stringify(currentContent.value) !== JSON.stringify(lastSavedContent.value)
  })

  // Actions
  async function getModules(courseId) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await api.get(`courses/module/${courseId}`, headers)
      modules.value = response.data
      return response
    } catch (error) {
      console.error('Error fetching modules:', error)
      throw error
    }
  }

  async function createContent(contentData, url) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await api.post(url, { ...contentData }, headers)
      return response
    }
    catch (error) {
      console.error('Error creating content:', error)
      throw error
    }
  }

  async function updateContent(contentData, url) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await api.put(url, { ...contentData }, headers)
      return response
    }
    catch (error) {
      console.error('Error updating content:', error)
      throw error
    }
  }

  async function createModule(moduleData) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await axios.post('/api/v1/modules', moduleData, headers)
      modules.value.push(response.data)
      return response
    } catch (error) {
      console.error('Error creating module:', error)
      throw error
    }
  }

  async function updateModule(moduleId, moduleData) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await axios.put(`/api/v1/modules/${moduleId}`, moduleData, headers)
      const index = modules.value.findIndex(m => m.id === moduleId)
      if (index !== -1) {
        modules.value[index] = response.data
      }
      return response
    } catch (error) {
      console.error('Error updating module:', error)
      throw error
    }
  }

  async function deleteModule(moduleId) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      await api.delete(`/courses/module/${moduleId}`, headers)
      modules.value = modules.value.filter(m => m.id !== moduleId)
    } catch (error) {
      console.error('Error deleting module:', error)
      throw error
    }
  }

  async function publishContent(contentData) {
    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      const response = await axios.post('/api/v1/content', {
        ...contentData,
        status: 'published'
      }, headers)

      // Update module contents
      const moduleIndex = modules.value.findIndex(m => m.id === contentData.moduleId)
      if (moduleIndex !== -1) {
        modules.value[moduleIndex].contents.push(response.data)
      }

      lastSavedContent.value = response.data
      return response
    } catch (error) {
      console.error('Error publishing content:', error)
      throw error
    }
  }

  async function saveDraft(contentData) {
    try {
      const response = await axios.post('/api/v1/content/draft', contentData)
      lastSavedContent.value = response.data
      return response
    } catch (error) {
      console.error('Error saving draft:', error)
      throw error
    }
  }

  async function uploadFile(file, contentId) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(
        `/api/v1/content/${contentId}/file`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return response
    } catch (error) {
      console.error('Error uploading file:', error)
      throw error
    }
  }

  function setCurrentContent(content) {
    currentContent.value = content
    lastSavedContent.value = { ...content }
  }

  function addToHistory(content) {
    contentHistory.value.push({
      ...content,
      timestamp: new Date().toISOString()
    })
    // Keep only last 10 items in history
    if (contentHistory.value.length > 10) {
      contentHistory.value.shift()
    }
  }

  return {
    // State
    modules,
    currentContent,
    contentHistory,
    lastSavedContent,
    // Getters
    getModuleById,
    getContentByModule,
    hasUnsavedChanges,
    // Actions
    getModules,
    createModule,
    updateModule,
    deleteModule,
    publishContent,
    saveDraft,
    uploadFile,
    setCurrentContent,
    addToHistory,
    createContent,
    updateContent
  }
}) 