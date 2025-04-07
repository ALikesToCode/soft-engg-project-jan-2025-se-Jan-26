import { defineStore } from 'pinia'
import { ref, computed, watch, onMounted } from 'vue'
import useAuthStore from './useAuthStore'
import ChatService from '@/services/chat.service'

export const useChatStore = defineStore('chat', () => {
  // State
  const chatHistory = ref([])
  const currentChatId = ref(null)
  const currentContext = ref(null)
  const isOpen = ref(false)
  const isSplitScreen = ref(false)
  const isLoading = ref(false)
  const initialized = ref(false)
  const error = ref(null)

  // Auth store
  const authStore = useAuthStore()

  // Getters
  const currentChat = computed(() => {
    if (!currentChatId.value) return null
    return chatHistory.value.find(chat => chat.id === currentChatId.value) || null
  })

  const contextTitle = computed(() => {
    if (!currentContext.value) return null
    
    if (currentContext.value.type === 'course') {
      return `${currentContext.value.courseName}`
    } else if (currentContext.value.type === 'assignment') {
      return `Assignment: ${currentContext.value.title}`
    } else if (currentContext.value.type === 'quiz') {
      return `Quiz: ${currentContext.value.title}`
    }
    
    return currentContext.value.title || 'Context Chat'
  })

  // For debugging
  watch(isOpen, (newVal) => {
    console.log("Chat isOpen changed to:", newVal)
  })

  // Sync with localStorage
  watch(chatHistory, (newValue) => {
    try {
      localStorage.setItem('chatHistory', JSON.stringify(newValue))
    } catch (err) {
      console.error("Error saving chat history to localStorage:", err)
    }
  }, { deep: true })

  // Helper function to ensure a valid chat is selected
  function ensureValidChatSelected() {
    if (chatHistory.value.length === 0) {
      // Create a new chat if none exists
      startNewChat("New Conversation")
      return
    }
    
    if (!currentChatId.value || !chatHistory.value.find(chat => chat.id === currentChatId.value)) {
      // Select the first chat if current is invalid
      setCurrentChat(chatHistory.value[0].id)
    }
  }

  // Initialize chat store
  async function initialize() {
    if (initialized.value) return
    
    try {
      isLoading.value = true
      error.value = null
      
      if (authStore.isAuthenticated) {
        // Try to fetch from backend
        await fetchChatHistory()
      } else {
        // Load from localStorage if not authenticated
        loadFromLocalStorage()
      }
      
      // Ensure we have a valid chat selected
      ensureValidChatSelected()
      
      initialized.value = true
    } catch (err) {
      console.error("Error initializing chat store:", err)
      error.value = "Failed to initialize chat store"
      
      // Fallback to localStorage
      loadFromLocalStorage()
      ensureValidChatSelected()
    } finally {
      isLoading.value = false
    }
  }

  // Load chat history from the backend
  async function fetchChatHistory() {
    try {
      if (!authStore.isAuthenticated) return
      
      isLoading.value = true
      error.value = null
      
      const response = await ChatService.getChatHistory()
      
      if (response && response.data && response.data.chatSessions) {
        chatHistory.value = response.data.chatSessions.map(session => ({
          id: session.id,
          title: session.title,
          createdAt: new Date(session.createdAt),
          lastUpdated: new Date(session.lastUpdated),
          messages: []
        }))
      }
    } catch (err) {
      console.error("Error fetching chat history:", err)
      error.value = "Failed to load chat history"
    } finally {
      isLoading.value = false
    }
  }

  // Load chat history from localStorage
  function loadFromLocalStorage() {
    try {
      const savedHistory = localStorage.getItem('chatHistory')
      if (savedHistory) {
        chatHistory.value = JSON.parse(savedHistory)
      }
    } catch (err) {
      console.error("Error loading chat history from localStorage:", err)
    }
  }

  // Add a message to a specific chat
  const addMessage = async (chatId, message) => {
    try {
      if (!chatId) return;
      
      // Find the chat in the history
      const chatIndex = chatHistory.value.findIndex(chat => chat.id === chatId);
      if (chatIndex === -1) return;
      
      // Add message to the chat
      if (!chatHistory.value[chatIndex].messages) {
        chatHistory.value[chatIndex].messages = [];
      }
      
      // Ensure message has the right format
      const formattedMessage = {
        id: message.id || Date.now() + '-' + (message.type || 'message'),
        type: message.type || (message.role === 'assistant' ? 'ai' : 'user'),
        role: message.role || (message.type === 'ai' ? 'assistant' : 'user'),
        content: message.content,
        timestamp: message.timestamp || new Date()
      };
      
      // Add to local state
      chatHistory.value[chatIndex].messages.push(formattedMessage);
      
      // Update lastUpdated time
      chatHistory.value[chatIndex].lastUpdated = new Date();
      
      // If authenticated, sync with backend
      if (authStore.isAuthenticated) {
        try {
          await ChatService.addMessage(chatId, formattedMessage);
        } catch (error) {
          console.error('Error adding message to backend:', error);
        }
      }
      
      return formattedMessage;
    } catch (error) {
      console.error('Error adding message:', error);
    }
  };

  // Start a new chat
  async function startNewChat(title = 'New Conversation') {
    try {
      isLoading.value = true
      error.value = null
      
      let newChat = null
      
      // Create in backend if authenticated
      if (authStore.isAuthenticated) {
        try {
          const response = await ChatService.createChatSession(title)
          
          if (response && response.data && response.data.chatSession) {
            newChat = {
              id: response.data.chatSession.id,
              title: response.data.chatSession.title,
              createdAt: new Date(response.data.chatSession.createdAt),
              lastUpdated: new Date(response.data.chatSession.lastUpdated),
              messages: []
            }
          }
        } catch (err) {
          console.error("Error creating chat in backend:", err)
        }
      }
      
      // Create locally if backend fails or not authenticated
      if (!newChat) {
        newChat = {
          id: 'local-' + Date.now(),
          title,
          createdAt: new Date(),
          lastUpdated: new Date(),
          messages: []
        }
      }
      
      // Add to history and select
      chatHistory.value.unshift(newChat)
      currentChatId.value = newChat.id
      
      return newChat
    } catch (err) {
      console.error("Error starting new chat:", err)
      error.value = "Failed to create new chat"
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Set the current chat
  async function setCurrentChat(chatId) {
    try {
      if (!chatId) return
      
      const chat = chatHistory.value.find(c => c.id === chatId)
      
      if (!chat) {
        throw new Error(`Chat with ID ${chatId} not found`)
      }
      
      currentChatId.value = chatId
      
      // Load messages if they don't exist and we're authenticated
      if (authStore.isAuthenticated && (!chat.messages || chat.messages.length === 0)) {
        try {
          const response = await ChatService.getMessages(chatId)
          
          if (response && response.data && response.data.messages) {
            chat.messages = response.data.messages.map(msg => ({
              id: msg.id,
              role: msg.role,
              content: msg.content,
              timestamp: new Date(msg.timestamp)
            }))
          }
        } catch (err) {
          console.error("Error loading messages from backend:", err)
        }
      }
    } catch (err) {
      console.error("Error setting current chat:", err)
      error.value = "Failed to load chat"
    }
  }

  // Update a chat's title
  async function updateChatTitle(chatId, newTitle) {
    try {
      if (!chatId) return
      
      const chat = chatHistory.value.find(c => c.id === chatId)
      
      if (!chat) {
        throw new Error(`Chat with ID ${chatId} not found`)
      }
      
      // Update in backend if authenticated
      if (authStore.isAuthenticated) {
        try {
          await ChatService.updateChatSession(chatId, { title: newTitle })
        } catch (err) {
          console.error("Error updating chat title in backend:", err)
        }
      }
      
      // Update locally
      chat.title = newTitle
      chat.lastUpdated = new Date()
    } catch (err) {
      console.error("Error updating chat title:", err)
    }
  }

  // Delete a chat
  async function deleteChat(chatId) {
    try {
      if (!chatId) return
      
      isLoading.value = true
      error.value = null
      
      // Delete from backend if authenticated
      if (authStore.isAuthenticated) {
        try {
          await ChatService.deleteChatSession(chatId)
        } catch (err) {
          console.error("Error deleting chat from backend:", err)
        }
      }
      
      // Remove from local state
      chatHistory.value = chatHistory.value.filter(chat => chat.id !== chatId)
      
      // If we deleted the current chat, select another one
      if (currentChatId.value === chatId) {
        ensureValidChatSelected()
      }
    } catch (err) {
      console.error("Error deleting chat:", err)
      error.value = "Failed to delete chat"
    } finally {
      isLoading.value = false
    }
  }

  // Clear all messages from a chat but keep the chat
  async function clearChatHistory(chatId) {
    try {
      if (!chatId) return
      
      isLoading.value = true
      error.value = null
      
      // First clear messages in local state to ensure UI responsiveness
      const chatIndex = chatHistory.value.findIndex(chat => chat.id === chatId)
      if (chatIndex !== -1) {
        chatHistory.value[chatIndex].messages = []
        chatHistory.value[chatIndex].lastUpdated = new Date()
      }
      
      // Then try to clear from backend if authenticated
      if (authStore.isAuthenticated) {
        try {
          await ChatService.clearChatHistory(chatId)
        } catch (err) {
          console.error("Error clearing chat history from backend:", err)
          // Don't set error.value since we successfully cleared locally
        }
      }
    } catch (err) {
      console.error("Error in clearChatHistory:", err)
      error.value = "Failed to clear chat history"
    } finally {
      isLoading.value = false
    }
  }

  // Toggle chat visibility
  function toggleChat() {
    isOpen.value = !isOpen.value
    console.log("Chat visibility toggled to:", isOpen.value)
    
    if (isOpen.value) {
      ensureValidChatSelected()
  }
  }

  // Open the chat
  function openChat() {
    ensureValidChatSelected()
    isOpen.value = true
    console.log("Chat opened, open state:", isOpen.value)
  }

  // Close the chat
  function closeChat() {
    isOpen.value = false
    console.log("Chat closed, open state:", isOpen.value)
  }

  // Toggle split screen mode
  function toggleSplitScreen() {
    isSplitScreen.value = !isSplitScreen.value
  }

  // Set chat context (course, assignment, etc.)
  function setContext(context) {
    currentContext.value = context
  }

  // Clear chat context
  function clearContext() {
    currentContext.value = null
  }

  return {
    // State
    chatHistory,
    currentChatId,
    currentContext,
    isOpen,
    isSplitScreen,
    isLoading,
    initialized,
    error,
    
    // Getters
    currentChat,
    contextTitle,
    
    // Actions
    initialize,
    fetchChatHistory,
    addMessage,
    startNewChat,
    setCurrentChat,
    updateChatTitle,
    deleteChat,
    clearChatHistory,
    toggleChat,
    openChat,
    closeChat,
    toggleSplitScreen,
    setContext,
    clearContext,
    ensureValidChatSelected
  }
}) 