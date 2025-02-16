import { defineStore } from 'pinia'
import axios from 'axios'

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [],
    currentCourse: null,
    loading: false,
    error: null
  }),

  getters: {
    getCourseById: (state) => (id) => {
      return state.courses.find(course => course.id === id)
    },
    
    facultyCourses: (state) => {
      return state.courses.filter(course => course.role === 'faculty')
    },
    
    activeCourses: (state) => {
      return state.courses.filter(course => course.status === 'active')
    }
  },

  actions: {
    async fetchCourses() {
      try {
        this.loading = true
        const response = await axios.get('/api/v1/courses')
        this.courses = response.data
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getFacultyCourses() {
      try {
        this.loading = true
        const response = await axios.get('/api/v1/faculty/courses')
        this.courses = response.data
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createCourse(courseData) {
      try {
        this.loading = true
        const response = await axios.post('/api/v1/courses', courseData)
        this.courses.push(response.data)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateCourse(courseId, courseData) {
      try {
        this.loading = true
        const response = await axios.put(`/api/v1/courses/${courseId}`, courseData)
        const index = this.courses.findIndex(c => c.id === courseId)
        if (index !== -1) {
          this.courses[index] = response.data
        }
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteCourse(courseId) {
      try {
        this.loading = true
        await axios.delete(`/api/v1/courses/${courseId}`)
        this.courses = this.courses.filter(c => c.id !== courseId)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentCourse(course) {
      this.currentCourse = course
    },

    clearError() {
      this.error = null
    }
  }
}) 