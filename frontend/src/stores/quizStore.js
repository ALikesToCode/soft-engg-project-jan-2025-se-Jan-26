import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { QuizService } from '@/services/quiz.service'
import { Quiz } from '@/models/Quiz'

export const useQuizStore = defineStore('quiz', () => {
  // State
  const quizzes = ref([])
  const currentQuiz = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const getQuizById = computed(() => (id) => {
    const quiz = quizzes.value.find(quiz => quiz.id === id)
    return quiz ? new Quiz(quiz) : null
  })
  
  const getQuizzesByModule = computed(() => (moduleId) => {
    return quizzes.value
      .filter(quiz => quiz.moduleId === moduleId)
      .map(quiz => new Quiz(quiz))
  })
  
  const getActiveQuizzes = computed(() => {
    return quizzes.value
      .filter(quiz => quiz.status === 'published')
      .map(quiz => new Quiz(quiz))
  })

  // Actions
  async function fetchQuizzes(courseId) {
    try {
      loading.value = true
      const response = await QuizService.fetchQuizzes(courseId)
      quizzes.value = response.data.map(quiz => new Quiz(quiz))
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createQuiz(quizData) {
    try {
      loading.value = true
      const quiz = new Quiz(quizData)
      if (!quiz.isValid()) {
        throw new Error('Invalid quiz data')
      }
      const response = await QuizService.createQuiz(quiz.toJSON())
      quizzes.value.push(new Quiz(response.data))
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateQuiz(quizId, quizData) {
    try {
      loading.value = true
      const quiz = new Quiz(quizData)
      if (!quiz.isValid()) {
        throw new Error('Invalid quiz data')
      }
      const response = await QuizService.updateQuiz(quizId, quiz.toJSON())
      const index = quizzes.value.findIndex(q => q.id === quizId)
      if (index !== -1) {
        quizzes.value[index] = new Quiz(response.data)
      }
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteQuiz(quizId) {
    try {
      loading.value = true
      await QuizService.deleteQuiz(quizId)
      quizzes.value = quizzes.value.filter(q => q.id !== quizId)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function submitQuiz(quizId, answers) {
    try {
      loading.value = true
      const response = await QuizService.submitQuiz(quizId, answers)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getQuizResults(quizId) {
    try {
      loading.value = true
      const response = await QuizService.getQuizResults(quizId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentQuiz(quiz) {
    currentQuiz.value = quiz ? new Quiz(quiz) : null
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    quizzes,
    currentQuiz,
    loading,
    error,
    // Getters
    getQuizById,
    getQuizzesByModule,
    getActiveQuizzes,
    // Actions
    fetchQuizzes,
    createQuiz,
    updateQuiz,
    deleteQuiz,
    submitQuiz,
    getQuizResults,
    setCurrentQuiz,
    clearError
  }
}) 