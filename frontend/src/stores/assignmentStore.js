import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AssignmentService } from '@/services/assignment.service'
import { Assignment } from '@/models/Assignment'

export const useAssignmentStore = defineStore('assignment', () => {
  const assignments = ref([])
  const currentAssignment = ref(null)
  const submissions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const getAssignmentById = computed(() => (id) => {
    const assignment = assignments.value.find(assignment => assignment.id === id)
    return assignment ? new Assignment(assignment) : null
  })
  
  const getAssignmentsByModule = computed(() => (moduleId) => {
    return assignments.value
      .filter(assignment => assignment.moduleId === moduleId)
      .map(assignment => new Assignment(assignment))
  })
  
  const getActiveAssignments = computed(() => {
    return assignments.value
      .filter(assignment => assignment.status === 'published')
      .map(assignment => new Assignment(assignment))
  })

  const getPendingSubmissions = computed(() => {
    return submissions.value.filter(submission => submission.status === 'pending')
  })

  const getGradedSubmissions = computed(() => {
    return submissions.value.filter(submission => submission.status === 'graded')
  })

  // Actions
  async function fetchAssignments(courseId) {
    try {
      loading.value = true
      const response = await AssignmentService.fetchAssignments(courseId)
      assignments.value = response.data.map(assignment => new Assignment(assignment))
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createAssignment(assignmentData) {
    try {
      loading.value = true
      const assignment = new Assignment(assignmentData)
      if (!assignment.isValid()) {
        throw new Error('Invalid assignment data')
      }
      const response = await AssignmentService.createAssignment(assignment.toJSON())
      assignments.value.push(new Assignment(response.data))
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateAssignment(assignmentId, assignmentData) {
    try {
      loading.value = true
      const assignment = new Assignment(assignmentData)
      if (!assignment.isValid()) {
        throw new Error('Invalid assignment data')
      }
      const response = await AssignmentService.updateAssignment(assignmentId, assignment.toJSON())
      const index = assignments.value.findIndex(a => a.id === assignmentId)
      if (index !== -1) {
        assignments.value[index] = new Assignment(response.data)
      }
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteAssignment(assignmentId) {
    try {
      loading.value = true
      await AssignmentService.deleteAssignment(assignmentId)
      assignments.value = assignments.value.filter(a => a.id !== assignmentId)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function submitAssignment(assignmentId, submissionData) {
    try {
      loading.value = true
      const response = await AssignmentService.submitAssignment(assignmentId, submissionData)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function gradeSubmission(assignmentId, submissionId, gradingData) {
    try {
      loading.value = true
      const response = await AssignmentService.gradeSubmission(assignmentId, submissionId, gradingData)
      
      const submissionIndex = submissions.value.findIndex(s => s.id === submissionId)
      if (submissionIndex !== -1) {
        submissions.value[submissionIndex] = response.data
      }
      
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSubmissions(assignmentId) {
    try {
      loading.value = true
      const response = await AssignmentService.fetchSubmissions(assignmentId)
      submissions.value = response.data
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getSubmissionDetails(assignmentId, submissionId) {
    try {
      loading.value = true
      const response = await AssignmentService.getSubmissionDetails(assignmentId, submissionId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function downloadSubmissionFile(assignmentId, submissionId) {
    try {
      loading.value = true
      const response = await AssignmentService.downloadSubmissionFile(assignmentId, submissionId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function getPlagiarismReport(assignmentId, submissionId) {
    try {
      loading.value = true
      const response = await AssignmentService.getPlagiarismReport(assignmentId, submissionId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentAssignment(assignment) {
    currentAssignment.value = assignment ? new Assignment(assignment) : null
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    assignments,
    currentAssignment,
    submissions,
    loading,
    error,
    // Getters
    getAssignmentById,
    getAssignmentsByModule,
    getActiveAssignments,
    getPendingSubmissions,
    getGradedSubmissions,
    // Actions
    fetchAssignments,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    submitAssignment,
    gradeSubmission,
    fetchSubmissions,
    getSubmissionDetails,
    downloadSubmissionFile,
    getPlagiarismReport,
    setCurrentAssignment,
    clearError
  }
}) 