import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'

export const CourseAssignmentService = {
  // Get all faculty-course assignments
  async getFacultyAssignments() {
    return axios.get(`${API_ROUTES.COURSES}/assignments`)
  },

  // Assign faculty to a course
  async assignFaculty(assignmentData) {
    return axios.post(`${API_ROUTES.COURSES}/assignments`, assignmentData)
  },

  // Remove faculty from a course
  async removeFacultyAssignment(assignmentId) {
    return axios.delete(`${API_ROUTES.COURSES}/assignments/${assignmentId}`)
  },

  // Bulk assign faculty to courses
  async bulkAssignFaculty(assignments) {
    return axios.post(`${API_ROUTES.COURSES}/assignments/bulk`, assignments)
  },

  // Get all available faculty members
  async getAvailableFaculty() {
    return axios.get(`${API_ROUTES.FACULTY}/available`)
  },

  // Get all courses
  async getCourses() {
    return axios.get(API_ROUTES.COURSES)
  },

  // Get course enrollment statistics
  async getCourseEnrollmentStats(courseId) {
    return axios.get(`${API_ROUTES.COURSES}/${courseId}/enrollment-stats`)
  },

  // Update course capacity
  async updateCourseCapacity(courseId, capacity) {
    return axios.put(`${API_ROUTES.COURSES}/${courseId}/capacity`, { capacity })
  }
} 