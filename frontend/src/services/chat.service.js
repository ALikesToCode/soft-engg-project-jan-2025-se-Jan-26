import axios from 'axios'
import { API_ROUTES } from '@/config/api.routes'
import { withLLMValidation } from '@/utils/llmValidator'
import api from '@/utils/api'

export const ChatService = {
  /**
   * Send a message to the AI and get a response
   * @param {Object} params - Object containing id and message
   * @param {string} params.id - Thread ID for conversation
   * @param {string} params.message - The user's message
   * @returns {Promise<Object>} - The AI's response
   */
  async sendMessage(params) {
    try {
      const { id, message } = typeof params === 'string' 
        ? { id: crypto.randomUUID(), message: params } 
        : params;
      
      const response = await api.post(`${API_ROUTES.LLM}/chat`, {
        id: id,
        query: message
      })
      return response.data
    } catch (error) {
      console.error('Error sending message to AI:', error)
      throw error
    }
  },

  /**
   * Get the current chat history
   * @returns {Promise<Array>} - The chat history
   */
  async getChatHistory() {
    try {
      const response = await axios.get(`${API_ROUTES.LLM}/chat`)
      return response.data
    } catch (error) {
      console.error('Error getting chat history:', error)
      throw error
    }
  },

  /**
   * Get available functions that the AI can call
   * @returns {Promise<Array>} - The available functions
   */
  async getAvailableFunctions() {
    try {
      const response = await axios.get(`${API_ROUTES.LLM}/available-functions`)
      return response.data
    } catch (error) {
      console.error('Error getting available functions:', error)
      throw error
    }
  },

  /**
   * Send a message to the AI with academic integrity validation
   * @param {Object|string} params - Either a string message or object with id and message
   * @returns {Promise<Object>} - The AI's response
   */
  sendValidatedMessage: withLLMValidation(async (params) => {
    try {
      const { id, message } = typeof params === 'string' 
        ? { id: crypto.randomUUID(), message: params } 
        : params;
      
      const response = await axios.post(`${API_ROUTES.LLM}/chat`, {
        id: id,
        query: message
      })
      return response.data
    } catch (error) {
      console.error('Error sending validated message to AI:', error)
      throw error
    }
  })
}

export default ChatService 