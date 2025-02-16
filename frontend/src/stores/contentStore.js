import { defineStore } from 'pinia'
import axios from 'axios'

export const useContentStore = defineStore('content', {
  state: () => ({
    modules: [],
    currentContent: null,
    contentHistory: [],
    lastSavedContent: null
  }),

  getters: {
    getModuleById: (state) => (id) => {
      return state.modules.find(module => module.id === id)
    },
    
    getContentByModule: (state) => (moduleId) => {
      return state.modules.find(m => m.id === moduleId)?.contents || []
    },

    hasUnsavedChanges: (state) => {
      return JSON.stringify(state.currentContent) !== JSON.stringify(state.lastSavedContent)
    }
  },

  actions: {
    async getModules(courseId) {
      try {
        const response = await axios.get(`/api/v1/courses/${courseId}/modules`)
        this.modules = response.data
        return response
      } catch (error) {
        console.error('Error fetching modules:', error)
        throw error
      }
    },

    async createModule(moduleData) {
      try {
        const response = await axios.post('/api/v1/modules', moduleData)
        this.modules.push(response.data)
        return response
      } catch (error) {
        console.error('Error creating module:', error)
        throw error
      }
    },

    async updateModule(moduleId, moduleData) {
      try {
        const response = await axios.put(`/api/v1/modules/${moduleId}`, moduleData)
        const index = this.modules.findIndex(m => m.id === moduleId)
        if (index !== -1) {
          this.modules[index] = response.data
        }
        return response
      } catch (error) {
        console.error('Error updating module:', error)
        throw error
      }
    },

    async deleteModule(moduleId) {
      try {
        await axios.delete(`/api/v1/modules/${moduleId}`)
        this.modules = this.modules.filter(m => m.id !== moduleId)
      } catch (error) {
        console.error('Error deleting module:', error)
        throw error
      }
    },

    async publishContent(contentData) {
      try {
        const response = await axios.post('/api/v1/content', {
          ...contentData,
          status: 'published'
        })
        
        // Update module contents
        const moduleIndex = this.modules.findIndex(m => m.id === contentData.moduleId)
        if (moduleIndex !== -1) {
          this.modules[moduleIndex].contents.push(response.data)
        }
        
        this.lastSavedContent = response.data
        return response
      } catch (error) {
        console.error('Error publishing content:', error)
        throw error
      }
    },

    async saveDraft(contentData) {
      try {
        const response = await axios.post('/api/v1/content/draft', contentData)
        this.lastSavedContent = response.data
        return response
      } catch (error) {
        console.error('Error saving draft:', error)
        throw error
      }
    },

    async uploadFile(file, contentId) {
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
    },

    setCurrentContent(content) {
      this.currentContent = content
      this.lastSavedContent = { ...content }
    },

    addToHistory(content) {
      this.contentHistory.push({
        ...content,
        timestamp: new Date().toISOString()
      })
      // Keep only last 10 items in history
      if (this.contentHistory.length > 10) {
        this.contentHistory.shift()
      }
    }
  }
}) 