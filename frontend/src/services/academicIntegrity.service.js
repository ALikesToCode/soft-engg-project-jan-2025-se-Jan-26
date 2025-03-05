import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'

export const AcademicIntegrityService = {
  // Get all flagged interactions
  async getFlaggedInteractions(filters = {}) {
    return axios.get(`${API_ROUTES.ACADEMIC_INTEGRITY}/flags`, { params: filters })
  },

  // Update flag status
  async updateFlagStatus(flagId, status, comment) {
    return axios.put(`${API_ROUTES.ACADEMIC_INTEGRITY}/flags/${flagId}`, {
      status,
      comment
    })
  },

  // Escalate a flagged item
  async escalateFlag(flagId, escalationDetails) {
    return axios.post(`${API_ROUTES.ACADEMIC_INTEGRITY}/flags/${flagId}/escalate`, escalationDetails)
  },

  // Get flag statistics
  async getFlagStatistics(courseId) {
    return axios.get(`${API_ROUTES.ACADEMIC_INTEGRITY}/statistics/${courseId}`)
  },

  // Get audit trail for a flag
  async getFlagAuditTrail(flagId) {
    return axios.get(`${API_ROUTES.ACADEMIC_INTEGRITY}/flags/${flagId}/audit`)
  },

  // Validate LLM request for academic integrity concerns
  async validateLLMRequest(requestContent) {
    try {
      const response = await axios.post(`${API_ROUTES.ACADEMIC_INTEGRITY}/validate-llm-request`, {
        content: requestContent
      })
      return response.data
    } catch (error) {
      console.error('Error validating LLM request:', error)
      // Return a safe default that blocks the request if validation fails
      return {
        isValid: false,
        reason: 'Validation service error. Request blocked for safety.',
        containsSensitiveContent: true
      }
    }
  }
} 