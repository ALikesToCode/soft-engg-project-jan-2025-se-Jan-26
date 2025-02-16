import { defineStore } from 'pinia'
import { QuizService } from '@/services/quiz.service'
import { Quiz } from '@/models/Quiz'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    quizzes: [],
    currentQuiz: null,
    loading: false,
    error: null
  }),

  getters: {
    getQuizById: (state) => (id) => {
      const quiz = state.quizzes.find(quiz => quiz.id === id)
      return quiz ? new Quiz(quiz) : null
    },
    
    getQuizzesByModule: (state) => (moduleId) => {
      return state.quizzes
        .filter(quiz => quiz.moduleId === moduleId)
        .map(quiz => new Quiz(quiz))
    },
    
    getActiveQuizzes: (state) => {
      return state.quizzes
        .filter(quiz => quiz.status === 'published')
        .map(quiz => new Quiz(quiz))
    }
  },

  actions: {
    async fetchQuizzes(courseId) {
      try {
        this.loading = true
        const response = await QuizService.fetchQuizzes(courseId)
        this.quizzes = response.data.map(quiz => new Quiz(quiz))
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createQuiz(quizData) {
      try {
        this.loading = true
        const quiz = new Quiz(quizData)
        if (!quiz.isValid()) {
          throw new Error('Invalid quiz data')
        }
        const response = await QuizService.createQuiz(quiz.toJSON())
        this.quizzes.push(new Quiz(response.data))
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateQuiz(quizId, quizData) {
      try {
        this.loading = true
        const quiz = new Quiz(quizData)
        if (!quiz.isValid()) {
          throw new Error('Invalid quiz data')
        }
        const response = await QuizService.updateQuiz(quizId, quiz.toJSON())
        const index = this.quizzes.findIndex(q => q.id === quizId)
        if (index !== -1) {
          this.quizzes[index] = new Quiz(response.data)
        }
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteQuiz(quizId) {
      try {
        this.loading = true
        await QuizService.deleteQuiz(quizId)
        this.quizzes = this.quizzes.filter(q => q.id !== quizId)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async submitQuiz(quizId, answers) {
      try {
        this.loading = true
        const response = await QuizService.submitQuiz(quizId, answers)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getQuizResults(quizId) {
      try {
        this.loading = true
        const response = await QuizService.getQuizResults(quizId)
        return response
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentQuiz(quiz) {
      this.currentQuiz = quiz ? new Quiz(quiz) : null
    },

    clearError() {
      this.error = null
    }
  }
}) 