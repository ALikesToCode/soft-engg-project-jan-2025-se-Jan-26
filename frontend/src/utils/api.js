import axios from 'axios'
import router from '@/router'
import { API_URL } from '@/config/constants'

// Create custom axios instance with the base URL
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor - add auth token to requests
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle common errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API error:', error.response || error.message)
    
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Only redirect to login if not already going there
      if (router.currentRoute.value.path !== '/login') {
        router.push({ path: '/login', query: { redirect: router.currentRoute.value.path } })
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
