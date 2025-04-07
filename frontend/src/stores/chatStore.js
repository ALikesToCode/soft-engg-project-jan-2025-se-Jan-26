import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ChatService } from '@/services/chat.service'

export const useChatStore = defineStore('chat', () => {
  const chats = ref([])
  const messages = ref({})
  const currentChatId = ref(null)
  const isOpen = ref(false)
  const contextTitle = ref('')
  const isSplitScreen = ref(false)

  // Create a new chat session
  const startNewChat = (title = 'New Chat') => {
    const id = crypto.randomUUID()
    
    chats.value.push({
      id,
      title,
      createdAt: new Date(),
      lastUpdated: new Date()
    })
    
    messages.value[id] = []
    currentChatId.value = id
    
    return id
  }
  
  // Get all chat sessions
  const getAllChats = () => {
    return chats.value
  }
  
  // Get a specific chat
  const getChat = (chatId) => {
    return chats.value.find(chat => chat.id === chatId) || null
  }
  
  // Get the current chat
  const getCurrentChat = computed(() => {
    if (!currentChatId.value) return null
    return getChat(currentChatId.value)
  })
  
  // Load a chat
  const loadChat = (chatId) => {
    const chat = getChat(chatId)
    if (chat) {
      currentChatId.value = chatId
      return true
    }
    return false
  }
  
  // Update a chat title
  const updateChatTitle = (chatId, title) => {
    const chatIndex = chats.value.findIndex(chat => chat.id === chatId)
    if (chatIndex !== -1) {
      chats.value[chatIndex].title = title
      chats.value[chatIndex].lastUpdated = new Date()
      return true
    }
    return false
  }
  
  // Delete a chat
  const deleteChat = (chatId) => {
    const chatIndex = chats.value.findIndex(chat => chat.id === chatId)
    if (chatIndex !== -1) {
      chats.value.splice(chatIndex, 1)
      delete messages.value[chatId]
      
      // If the deleted chat was the current one, clear the current chat
      if (currentChatId.value === chatId) {
        currentChatId.value = chats.value.length > 0 ? chats.value[0].id : null
      }
      
      return true
    }
    return false
  }
  
  // Add a message to a chat
  const addMessage = async (chatId, message) => {
    if (!messages.value[chatId]) {
      messages.value[chatId] = []
    }
    
    messages.value[chatId].push(message)
    
    // Update the chat's last updated timestamp
    const chatIndex = chats.value.findIndex(chat => chat.id === chatId)
    if (chatIndex !== -1) {
      chats.value[chatIndex].lastUpdated = new Date()
    }
    
    return message
  }
  
  // Get messages for a chat
  const getMessages = (chatId) => {
    if (!chatId) return []
    return messages.value[chatId] || []
  }
  
  // Clear all messages for a chat but keep the chat session
  const clearMessages = (chatId) => {
    if (messages.value[chatId]) {
      messages.value[chatId] = []
      
      // Update the chat's last updated timestamp
      const chatIndex = chats.value.findIndex(chat => chat.id === chatId)
      if (chatIndex !== -1) {
        chats.value[chatIndex].lastUpdated = new Date()
      }
      
      return true
    }
    return false
  }
  
  // Load chat history from storage
  const loadHistory = async () => {
    try {
      // Get all chat sessions
      const response = await ChatService.getChatSessions()
      if (response.data && response.data.chatSessions) {
        // Map API response to local format
        chats.value = response.data.chatSessions.map(chat => ({
          id: chat.id,
          title: chat.title,
          createdAt: new Date(chat.createdAt),
          lastUpdated: new Date(chat.lastUpdated)
        }))
        
        // Load messages for each chat
        for (const chat of chats.value) {
          const messagesResponse = await ChatService.getMessages(chat.id)
          if (messagesResponse.data && messagesResponse.data.messages) {
            messages.value[chat.id] = messagesResponse.data.messages.map(msg => ({
              id: msg.id,
              role: msg.role,
              type: msg.role === 'assistant' ? 'ai' : 'user',
              content: msg.content,
              timestamp: new Date(msg.timestamp)
            }))
          }
        }
        
        // Set current chat to the most recently updated one if we have chats
        if (chats.value.length > 0) {
          const sortedChats = [...chats.value].sort((a, b) => b.lastUpdated - a.lastUpdated)
          currentChatId.value = sortedChats[0].id
        }
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }
  
  return {
    chats,
    messages,
    currentChatId,
    isOpen,
    contextTitle,
    isSplitScreen,
    startNewChat,
    getAllChats,
    getChat,
    getCurrentChat,
    loadChat,
    updateChatTitle,
    deleteChat,
    addMessage,
    getMessages,
    clearMessages,
    loadHistory
  }
}) 