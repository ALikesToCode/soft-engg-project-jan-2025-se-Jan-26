import { defineStore } from 'pinia'
import useAuthStore from '@/stores/useAuthStore'

export const useChatStore = defineStore('chat', {
  state: () => ({
    isOpen: false,
    currentContext: null,
    chatHistory: [],
    isSplitScreen: false
  }),

  actions: {
    toggleChat() {
      this.isOpen = !this.isOpen
    },
    closeChat() {
      this.isOpen = false
    },
    openChat() {
      this.isOpen = true
    },
    setContext(context) {
      this.currentContext = context
      this.openChat()
    },
    toggleSplitScreen() {
      this.isSplitScreen = !this.isSplitScreen
      this.isOpen = true
    },
    addToHistory(message) {
      this.chatHistory.push(message)
    },
    clearContext() {
      this.currentContext = null
    }
  },

  getters: {
    contextTitle: (state) => {
      if (!state.currentContext) return 'Learning Assistant'
      return state.currentContext.title || 'Learning Assistant'
    },
    shouldShowChat: () => {
      const authStore = useAuthStore()
      return authStore.isAuthenticated
    }
  }
}) 