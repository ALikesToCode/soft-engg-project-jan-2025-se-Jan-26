import api from '@/utils/api'

/**
 * Service for executing API functions returned by the LLM
 */
export const ApiExecutorService = {
  /**
   * Map of function names to API configurations
   * Each entry contains path, method, and any special handling
   */
  functionMappings: {
    // Courses
    getCourses: { path: '/courses', method: 'GET' },
    getCourseById: { path: '/courses/{id}', method: 'GET' },
    
    // Assignments
    getAssignments: { path: '/assignments', method: 'GET' },
    getAssignmentById: { path: '/assignments/{id}', method: 'GET' },
    submitAssignment: { path: '/assignments/{id}/submit', method: 'POST' },
    
    // Academic Integrity
    checkPlagiarism: { path: '/academic-integrity/check', method: 'POST' },
    
    // FAQs
    getFaqs: { path: '/faqs', method: 'GET' },
    searchFaqs: { path: '/faqs/search', method: 'GET' },
    
    // User profile
    getUserProfile: { path: '/user/profile', method: 'GET' },
    updateUserProfile: { path: '/user/profile', method: 'PUT' },
    
    // Notifications
    getNotifications: { path: '/notifications', method: 'GET' },
    markNotificationRead: { path: '/notifications/{id}/read', method: 'PUT' },
    
    // Default handler for unknown functions (will be handled based on function name)
    default: { path: '/{function}', method: 'POST' }
  },

  /**
   * Execute an API function
   * 
   * @param {Object} functionCall - The function call object from the LLM
   * @param {string} functionCall.name - The name of the function to execute
   * @param {Object} functionCall.arguments - The arguments to pass to the function
   * @returns {Promise<Object>} - The result of the API call
   */
  async executeFunction(functionCall) {
    if (!functionCall || !functionCall.name) {
      throw new Error('Invalid function call')
    }
    
    const { name, arguments: args = {} } = functionCall
    
    // Get the function mapping
    const mapping = this.functionMappings[name] || this.functionMappings.default
    
    // Replace path parameters
    let path = mapping.path.replace('{function}', name.toLowerCase())
    
    // Replace path parameters with values from args
    Object.keys(args).forEach(key => {
      if (path.includes(`{${key}}`)) {
        path = path.replace(`{${key}}`, args[key])
        // Remove from args since it's used in the path
        delete args[key]
      }
    })
    
    // Configure request based on method
    try {
      let response
      
      switch (mapping.method) {
        case 'GET':
          // For GET, send args as query parameters
          response = await api.get(path, { params: args })
          break
          
        case 'POST':
          // For POST, send args as request body
          response = await api.post(path, args)
          break
          
        case 'PUT':
          // For PUT, send args as request body
          response = await api.put(path, args)
          break
          
        case 'DELETE':
          // For DELETE, send args as query parameters
          response = await api.delete(path, { params: args })
          break
          
        default:
          throw new Error(`Unsupported HTTP method: ${mapping.method}`)
      }
      
      return {
        function_name: name,
        success: true,
        result: response.data
      }
    } catch (error) {
      console.error(`Error executing API function ${name}:`, error)
      return {
        function_name: name,
        success: false,
        error: error.response?.data?.detail || error.message
      }
    }
  },

  /**
   * Execute multiple API functions
   * 
   * @param {Array} functionCalls - Array of function call objects from the LLM
   * @returns {Promise<Array>} - Results of all API calls
   */
  async executeFunctions(functionCalls) {
    if (!functionCalls || !functionCalls.length) {
      return []
    }
    
    const results = []
    
    for (const functionCall of functionCalls) {
      try {
        const result = await this.executeFunction(functionCall)
        results.push(result)
      } catch (error) {
        console.error(`Failed to execute function ${functionCall.name}:`, error)
        results.push({
          function_name: functionCall.name,
          success: false,
          error: error.message
        })
      }
    }
    
    return results
  }
}

export default ApiExecutorService 