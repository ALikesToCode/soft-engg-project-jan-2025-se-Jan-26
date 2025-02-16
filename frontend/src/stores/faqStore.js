import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

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
      const response = await axios.get('/api/v1/faqs')
      faqs.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createFaq(faqData) {
    try {
      loading.value = true
      const response = await axios.post('/api/v1/faqs', faqData)
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
      const response = await axios.put(`/api/v1/faqs/${faqId}`, faqData)
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
      await axios.delete(`/api/v1/faqs/${faqId}`)
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
      const response = await axios.post(`/api/v1/faqs/${faqId}/rate`, { isHelpful })
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