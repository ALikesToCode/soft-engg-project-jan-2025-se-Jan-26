import axios from 'axios'
import router from '@/router'
import { API_URL } from '@/config'

// Create custom axios instance with the base URL
const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // Increase timeout to 60 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor - add auth token to requests
api.interceptors.request.use(
  config => {
    // Add authorization token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    // Add a timestamp to prevent caching issues for GET requests
    if (config.method === 'get') {
      // Initialize params object if it doesn't exist
      config.params = config.params || {}

      // Only add timestamp if it hasn't been added manually
      // if (!config.params['_t']) {
      //   config.params['_t'] = Date.now()
      // }

      // Ensure Cache-Control header is set to prevent browser caching
      config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
      config.headers['Pragma'] = 'no-cache'
      config.headers['Expires'] = '0'
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
      console.error('Authentication error (401):', error.response.data || error.message)
      localStorage.removeItem('token')
      localStorage.removeItem('user')

      // Only redirect to login if not already going there
      if (router.currentRoute.value.path !== '/login') {
        router.push({ path: '/login', query: { redirect: router.currentRoute.value.path } })
      }
    } 
    // Handle server errors
    else if (error.response && error.response.status >= 500) {
      console.error('Server error:', error.response.status, error.response.data || error.message)
    } 
    // Handle network errors or timeouts
    else if (!error.response || error.code === 'ECONNABORTED') {
      console.error('Network error or timeout:', error.message || error)
      
      // Retry the request once for network issues
      try {
        // Create a new request with original config but increased timeout
        if (!error.config._isRetry) {
          console.log('Retrying failed request...')
          const config = {...error.config}
          config.timeout = 90000 // 90 seconds for retry attempts
          config._isRetry = true
          return await axios(config)
        }
      } catch (retryError) {
        console.error('Retry failed:', retryError)
      }
    } 
    // Handle other errors
    else {
      console.error('API error:', error.response?.status, error.response?.data || error.message)
    }

    return Promise.reject(error)
  }
)

export default api
