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
    
    // Add a timestamp to prevent caching issues
    if (config.method === 'get') {
      config.params = config.params || {}
      config.params['_t'] = Date.now()
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
  async error => {
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
    
    // Handle network errors with potential retry
    if (!error.response && error.code === 'ECONNABORTED') {
      console.log('Request timeout, retrying...')
      
      // Retry the request once
      try {
        // Create a new request with original config but increased timeout
        const config = {...error.config}
        config.timeout = config.timeout * 1.5 // Increase timeout for retry
        
        // Don't retry a failed retry
        if (config._isRetry) {
          throw error
        }
        
        config._isRetry = true
        return await axios(config)
      } catch (retryError) {
        console.error('Retry failed:', retryError)
        return Promise.reject(error) // Return original error if retry fails
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
