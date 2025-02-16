import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import useAuthStore from '@/stores/useAuthStore'

export const useChatStore = defineStore('chat', () => {
  // State
  const isOpen = ref(false)
  const currentContext = ref(null)
  const chatHistory = ref([])
  const isSplitScreen = ref(false)

  // Actions
  function toggleChat() {
    isOpen.value = !isOpen.value
  }

  function closeChat() {
    isOpen.value = false
  }

  function openChat() {
    isOpen.value = true
  }

  function setContext(context) {
    currentContext.value = context
    openChat()
  }

  function toggleSplitScreen() {
    isSplitScreen.value = !isSplitScreen.value
    isOpen.value = true
  }

  function addToHistory(message) {
    chatHistory.value.push(message)
  }

  function clearContext() {
    currentContext.value = null
  }

  // Getters
  const contextTitle = computed(() => {
    if (!currentContext.value) return 'Learning Assistant'
    return currentContext.value.title || 'Learning Assistant'
  })

  const shouldShowChat = computed(() => {
    const authStore = useAuthStore()
    return authStore.isAuthenticated
  })

  return {
    // State
    isOpen,
    currentContext,
    chatHistory,
    isSplitScreen,
    // Actions
    toggleChat,
    closeChat,
    openChat,
    setContext,
    toggleSplitScreen,
    addToHistory,
    clearContext,
    // Getters
    contextTitle,
    shouldShowChat
  }
}) 