import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'

export const AssignmentService = {
  async fetchAssignments(courseId) {
    return axios.get(`${API_ROUTES.ASSIGNMENTS}?course_id=${courseId}`)
  },

  async createAssignment(assignmentData) {
    return axios.post(`${API_ROUTES.ASSIGNMENTS}`, assignmentData)
  },

  async updateAssignment(assignmentId, assignmentData) {
    return axios.put(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}`, assignmentData)
  },

  async deleteAssignment(assignmentId) {
    return axios.delete(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}`)
  },

  async submitAssignment(assignmentId, submissionData) {
    const formData = new FormData()
    
    if (submissionData.file) {
      formData.append('file', submissionData.file)
    }
    
    Object.keys(submissionData).forEach(key => {
      if (key !== 'file') {
        formData.append(key, submissionData[key])
      }
    })

    return axios.post(
      `${API_ROUTES.ASSIGNMENTS}/${assignmentId}/submit`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
  },

  async gradeSubmission(assignmentId, submissionId, gradingData) {
    return axios.put(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}/grade/${submissionId}`, gradingData)
  },

  async fetchSubmissions(assignmentId) {
    return axios.get(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}/submissions`)
  },

  async getSubmissionDetails(assignmentId, submissionId) {
    return axios.get(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}/submissions/${submissionId}`)
  },
  
  async downloadSubmissionFile(assignmentId, submissionId) {
    return axios.get(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}/submissions/${submissionId}/download`, {
      responseType: 'blob'
    })
  },
  
  async getPlagiarismReport(assignmentId, submissionId) {
    return axios.get(`${API_ROUTES.ASSIGNMENTS}/${assignmentId}/submissions/${submissionId}/plagiarism`)
  }
} 