import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'

export const QuizService = {
  async fetchQuizzes(courseId) {
    return axios.get(`${API_ROUTES.COURSES}/${courseId}/quizzes`)
  },

  async createQuiz(quizData) {
    return axios.post(`${API_ROUTES.QUIZZES}`, quizData)
  },

  async updateQuiz(quizId, quizData) {
    return axios.put(`${API_ROUTES.QUIZZES}/${quizId}`, quizData)
  },

  async deleteQuiz(quizId) {
    return axios.delete(`${API_ROUTES.QUIZZES}/${quizId}`)
  },

  async submitQuiz(quizId, answers) {
    return axios.post(`${API_ROUTES.QUIZZES}/${quizId}/submit`, answers)
  },

  async getQuizResults(quizId) {
    return axios.get(`${API_ROUTES.QUIZZES}/${quizId}/results`)
  }
} 