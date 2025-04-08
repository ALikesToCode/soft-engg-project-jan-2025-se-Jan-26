import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import api from '@/utils/api'

export const useCourseStore = defineStore('course', () => {
  // State
  const courses = ref([])
  const currentCourse = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const course_id = ref(null)

  // Getters
  const getCourseById = computed(() => (id) => {
    return courses.value.find(course => course.id === id)
  })

  const facultyCourses = computed(() => {
    return courses.value.filter(course => course.role === 'faculty')
  })

  const activeCourses = computed(() => {
    return courses.value.filter(course => course.status === 'active')
  })

  // Actions
  async function fetchCourses() {
    try {
      loading.value = true
      const response = await api.get('/courses')
      courses.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Add getUserCourses method - same implementation as fetchCourses
  async function getUserCourses() {
    try {
      loading.value = true
      const response = await api.get('/courses', {
        params: { 
          _t: Date.now() // Add timestamp to prevent caching
        }
      })
      courses.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      console.error('Error fetching user courses:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getFacultyCourses() {
    try {
      loading.value = true
      // Don't add custom headers, let the api interceptor handle the authorization
      // This was causing an issue with the cache busting timestamp
      const response = await api.get('/faculty/courses', {
        params: {
          _t: Date.now() // Explicitly add timestamp to prevent caching
        }
      })
      console.log('Faculty courses response:', response.data)
      courses.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      console.error('Error fetching faculty courses:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCourse(courseData) {
    try {
      loading.value = true
      const response = await api.post('/courses', courseData)
      courses.value.push(response.data)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCourse(courseId, courseData) {
    try {
      loading.value = true
      const response = await api.put(`/courses/${courseId}`, courseData)
      const index = courses.value.findIndex(c => c.id === courseId)
      if (index !== -1) {
        courses.value[index] = response.data
      }
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCourse(courseId) {
    try {
      loading.value = true
      await api.delete(`/courses/${courseId}`)
      courses.value = courses.value.filter(c => c.id !== courseId)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentCourse(course) {
    currentCourse.value = course
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    courses,
    currentCourse,
    loading,
    error,
    // Getters
    getCourseById,
    facultyCourses,
    activeCourses,
    // Actions
    fetchCourses,
    getUserCourses,
    getFacultyCourses,
    createCourse,
    updateCourse,
    deleteCourse,
    setCurrentCourse,
    clearError
  }
}) 