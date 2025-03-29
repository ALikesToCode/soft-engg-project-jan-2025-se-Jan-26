import axios from 'axios'
import api from '@/utils/api'
import { API_ROUTES } from '@/config/api.routes'

// Fixing API paths by removing duplicate /api/v1/
const API_PATH_ACADEMIC_INTEGRITY = '/academic-integrity';

export const AcademicIntegrityService = {
  // Get all flagged interactions
  async getFlaggedInteractions(filters = {}) {
    return api.get(`${API_PATH_ACADEMIC_INTEGRITY}/flags`, { params: filters })
  },

  // Update flag status
  async updateFlagStatus(flagId, status, comment) {
    return api.put(`${API_PATH_ACADEMIC_INTEGRITY}/flags/${flagId}`, {
      status,
      comment
    })
  },

  // Escalate a flagged item
  async escalateFlag(flagId, escalationDetails) {
    return api.post(`${API_PATH_ACADEMIC_INTEGRITY}/flags/${flagId}/escalate`, escalationDetails)
  },

  // Get flag statistics
  async getFlagStatistics(courseId) {
    return api.get(`${API_PATH_ACADEMIC_INTEGRITY}/statistics/${courseId}`)
  },

  // Get audit trail for a flag
  async getFlagAuditTrail(flagId) {
    return api.get(`${API_PATH_ACADEMIC_INTEGRITY}/flags/${flagId}/audit`)
  },

  // Validate LLM request for academic integrity concerns
  async validateLLMRequest(requestContent) {
    try {
      const response = await api.post(`${API_PATH_ACADEMIC_INTEGRITY}/validate-llm-request`, {
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
  },
  
  // Check LLM response for academic integrity issues
  async checkLLMResponse(data) {
    try {
      const response = await api.post(`${API_PATH_ACADEMIC_INTEGRITY}/check-llm-response`, {
        response: data.response,
        query: data.query,
        course_context: data.course_context
      })
      return response.data
    } catch (error) {
      console.error('Error checking LLM response for integrity issues:', error)
      // Generate a fallback response
      return {
        flagged: false,
        integrity_score: 100,
        analysis: {
          summary: "Integrity check failed. The response could not be analyzed.",
          flags: []
        }
      }
    }
  }
} 