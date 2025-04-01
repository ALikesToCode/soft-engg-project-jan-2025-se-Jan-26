import api from '@/utils/api'
import { API_ROUTES } from '@/config/api.routes'

export const CourseAssignmentService = {
  // Get all faculty-course assignments
  async getFacultyAssignments() {
    return api.get(`${API_ROUTES.COURSES}/assignments`)
  },

  // Assign faculty to a course
  async assignFaculty(assignmentData) {
    return api.post(`${API_ROUTES.COURSES}/assignments`, assignmentData)
  },

  // Remove faculty from a course
  async removeFacultyAssignment(assignmentId) {
    return api.delete(`${API_ROUTES.COURSES}/assignments/${assignmentId}`)
  },

  // Bulk assign faculty to courses
  async bulkAssignFaculty(assignments) {
    return api.post(`${API_ROUTES.COURSES}/assignments/bulk`, assignments)
  },

  // Get all available faculty members
  async getAvailableFaculty() {
    return api.get(`${API_ROUTES.FACULTY}/available`)
  },

  // Get all courses
  async getCourses() {
    return api.get(API_ROUTES.COURSES)
  },

  // Get course enrollment statistics
  async getCourseEnrollmentStats(courseId) {
    return api.get(`${API_ROUTES.COURSES}/${courseId}/enrollment-stats`)
  },

  // Update course capacity
  async updateCourseCapacity(courseId, capacity) {
    return api.put(`${API_ROUTES.COURSES}/${courseId}/capacity`, { capacity })
  }
} 