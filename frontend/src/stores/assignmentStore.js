import { defineStore } from 'pinia'
import { AssignmentService } from '@/services/assignment.service'
import { Assignment } from '@/models/Assignment'

export const useAssignmentStore = defineStore('assignment', {
  state: () => ({
    assignments: [],
    currentAssignment: null,
    submissions: [],
    loading: false,
    error: null
  }),

  getters: {
    getAssignmentById: (state) => (id) => {
      const assignment = state.assignments.find(assignment => assignment.id === id)
      return assignment ? new Assignment(assignment) : null
    },
    
    getAssignmentsByModule: (state) => (moduleId) => {
      return state.assignments
        .filter(assignment => assignment.moduleId === moduleId)
        .map(assignment => new Assignment(assignment))
    },
    
    getActiveAssignments: (state) => {
      return state.assignments
        .filter(assignment => assignment.status === 'published')
        .map(assignment => new Assignment(assignment))
    },

    getPendingSubmissions: (state) => {
      return state.submissions.filter(submission => submission.status === 'pending')
    },

    getGradedSubmissions: (state) => {
      return state.submissions.filter(submission => submission.status === 'graded')
    }
  },

  actions: {
    async fetchAssignments(courseId) {
      try {
        this.loading = true
        const response = await AssignmentService.fetchAssignments(courseId)
        this.assignments = response.data.map(assignment => new Assignment(assignment))
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createAssignment(assignmentData) {
      try {
        this.loading = true
        const assignment = new Assignment(assignmentData)
        if (!assignment.isValid()) {
          throw new Error('Invalid assignment data')
        }
        const response = await AssignmentService.createAssignment(assignment.toJSON())
        this.assignments.push(new Assignment(response.data))
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateAssignment(assignmentId, assignmentData) {
      try {
        this.loading = true
        const assignment = new Assignment(assignmentData)
        if (!assignment.isValid()) {
          throw new Error('Invalid assignment data')
        }
        const response = await AssignmentService.updateAssignment(assignmentId, assignment.toJSON())
        const index = this.assignments.findIndex(a => a.id === assignmentId)
        if (index !== -1) {
          this.assignments[index] = new Assignment(response.data)
        }
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteAssignment(assignmentId) {
      try {
        this.loading = true
        await AssignmentService.deleteAssignment(assignmentId)
        this.assignments = this.assignments.filter(a => a.id !== assignmentId)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async submitAssignment(assignmentId, submissionData) {
      try {
        this.loading = true
        const response = await AssignmentService.submitAssignment(assignmentId, submissionData)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async gradeSubmission(submissionId, gradingData) {
      try {
        this.loading = true
        const response = await AssignmentService.gradeSubmission(submissionId, gradingData)
        
        const submissionIndex = this.submissions.findIndex(s => s.id === submissionId)
        if (submissionIndex !== -1) {
          this.submissions[submissionIndex] = response.data
        }
        
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchSubmissions(assignmentId) {
      try {
        this.loading = true
        const response = await AssignmentService.fetchSubmissions(assignmentId)
        this.submissions = response.data
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getSubmissionDetails(submissionId) {
      try {
        this.loading = true
        const response = await AssignmentService.getSubmissionDetails(submissionId)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentAssignment(assignment) {
      this.currentAssignment = assignment ? new Assignment(assignment) : null
    },

    clearError() {
      this.error = null
    }
  }
}) 