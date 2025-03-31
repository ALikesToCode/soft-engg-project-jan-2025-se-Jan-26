import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL
const API_PREFIX = import.meta.env.VITE_API_PREFIX || ''

export const useFaqStore = defineStore('faq', () => {
  // State
  const faqs = ref([])
  const loading = ref(false)
  const error = ref(null)
  const categories = ref([
    { id: 'all', name: 'All Topics' },
    { id: 'general', name: 'General' },
    { id: 'technical', name: 'Technical' },
    { id: 'courses', name: 'Courses' },
    { id: 'account', name: 'Account' },
    { id: 'faculty', name: 'Faculty' }
  ])

  // Getters
  const getFaqById = computed(() => (id) => {
    return faqs.value.find(faq => faq.id === id)
  })

  const getFaqsByCategory = computed(() => (categoryId) => {
    if (categoryId === 'all') return faqs.value
    return faqs.value.filter(faq => faq.categoryId === categoryId)
  })

  const getCategories = computed(() => {
    return categories.value.filter(c => c.id !== 'all')
  })

  // Actions
  async function fetchFaqs() {
    try {
      loading.value = true
      const token = localStorage.getItem('token');
      // console.log('Token:', token);
      const response = await axios.get(`${API_URL}${API_PREFIX}/faqs/faqs`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      faqs.value = response.data
      return response
    } catch (err) {
      console.error('Error fetching users:', err)
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createFaq(faqData) {
    try {
      loading.value = true
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}${API_PREFIX}/faqs/faqs`, faqData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      faqs.value.push(response.data)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateFaq(faqId, faqData) {
    try {
      loading.value = true
      const token = localStorage.getItem('token');
      const response = await axios.put(`${API_URL}${API_PREFIX}/faqs/faqs/${faqId}`, faqData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      const index = faqs.value.findIndex(f => f.id === faqId)
      if (index !== -1) {
        faqs.value[index] = response.data
      }
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteFaq(faqId) {
    try {
      loading.value = true
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}${API_PREFIX}/faqs/faqs/${faqId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      faqs.value = faqs.value.filter(f => f.id !== faqId)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function rateFaq(faqId, isHelpful) {
    try {
      loading.value = true
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}${API_PREFIX}/faqs/faqs/${faqId}/rate`, { isHelpful }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      const index = faqs.value.findIndex(f => f.id === faqId)
      if (index !== -1) {
        faqs.value[index] = {
          ...faqs.value[index],
          ratings: response.data.ratings
        }
      }
      return response
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
    faqs,
    loading,
    error,
    categories,
    // Getters
    getFaqById,
    getFaqsByCategory,
    getCategories,
    // Actions
    fetchFaqs,
    createFaq,
    updateFaq,
    deleteFaq,
    rateFaq,
    clearError
  }
}) 