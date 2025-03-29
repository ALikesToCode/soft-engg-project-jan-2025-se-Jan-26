<template>
  <div class="chat-container">
    <!-- Chat Panel -->
    <Teleport to="body">
      <div 
        v-if="isOpen"
        class="chat-panel"
        :class="{ 'full-screen': isSplitScreen }"
    >
      <!-- Chat Header -->
        <div class="chat-header">
          <div class="flex items-center gap-3">
            <button
              @click="toggleHistory"
              class="icon-button"
              :class="{ 'active': showHistory }"
              aria-label="Chat History"
            >
              <span class="material-icons">history</span>
            </button>
            <h2 class="chat-title">{{ chatTitle }}</h2>
            <div 
            v-if="chatStore.currentContext"
              class="context-badge"
          >
            {{ chatStore.currentContext.type }}
            </div>
            <div v-if="canUseFunctions" class="function-badge" title="This AI can use functions to retrieve information">
              <span class="material-icons function-icon">functions</span>
              <span>Functions</span>
            </div>
        </div>
          <div class="flex items-center gap-2">
          <button 
              @click="toggleSplitScreen"
              class="icon-button"
              aria-label="Toggle Split Screen"
          >
            <span class="material-icons">{{ chatStore.isSplitScreen ? 'close_fullscreen' : 'open_in_full' }}</span>
          </button>
          <button 
              @click="closeChat"
              class="icon-button"
              aria-label="Close Chat"
          >
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>

        <!-- Chat History Sidebar -->
        <Transition name="slide-left">
          <div
            v-if="showHistory"
            class="history-sidebar"
          >
            <div class="history-header">
              <h3 class="history-title">Conversations</h3>
              <button @click="toggleHistory" class="icon-button" aria-label="Close History">
                <span class="material-icons">close</span>
              </button>
            </div>
            <div class="p-4">
              <button
                @click="startNewChat"
                class="new-chat-button"
              >
                <span class="material-icons text-sm mr-2">add</span>
                New Conversation
              </button>
            </div>
            <div class="history-list">
              <div v-if="chatStore.chatHistory.length === 0" class="empty-state">
                <span class="material-icons text-3xl mb-2 text-gray-400">chat_bubble_outline</span>
                <p>No conversations yet</p>
              </div>
              <ul v-else class="chat-list">
                <li 
                  v-for="chat in chatStore.chatHistory" 
                  :key="chat.id" 
                  class="chat-list-item"
                  :class="{ 'selected': chatStore.currentChatId === chat.id }"
                  @click="selectChat(chat.id)"
                >
                  <div class="flex justify-between items-center w-full">
                    <div class="flex-1 min-w-0">
                      <h4 class="chat-item-title">{{ chat.title }}</h4>
                      <p class="chat-item-date">{{ formatDate(chat.lastUpdated) }}</p>
                    </div>
                    <button
                      @click.stop="deleteChat(chat.id)"
                      class="delete-button"
                      aria-label="Delete Conversation"
                    >
                      <span class="material-icons text-sm">delete</span>
                    </button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </Transition>

      <!-- Chat Content -->
      <ChatBotBox 
          class="chat-content" 
        :context="chatStore.currentContext"
          :chat-id="chatStore.currentChatId"
        @clear-context="chatStore.clearContext"
          @update:title="chatStore.updateChatTitle"
      />
    </div>
    </Teleport>

    <!-- Chat Toggle Button -->
    <Transition name="fade">
    <button
        v-if="!isOpen && shouldShowButton && isAuthenticated && !isPublicRoute"
        @click="openChat"
        class="chat-toggle-button"
        aria-label="Open Chat"
    >
      <span class="material-icons">chat</span>
        <span class="chat-tooltip">
        Ask Learning Assistant
      </span>
    </button>
    </Transition>
  </div>
</template>

<script>
import { useChatStore } from '@/stores/useChatStore'
import { useRoute } from 'vue-router'
import { computed, onMounted, ref, watch } from 'vue'
import ChatBotBox from './ChatBotBox.vue'
import useAuthStore from '@/stores/useAuthStore'
import ChatService from '@/services/chat.service'

export default {
  name: 'GlobalChat',
  components: {
    ChatBotBox
  },
  setup() {
    const chatStore = useChatStore()
    const authStore = useAuthStore()
    const route = useRoute()

    // Local state
    const isOpen = ref(false)
    const showHistory = ref(false)
    const shouldShowButton = ref(true)
    const isSplitScreen = computed(() => chatStore.isSplitScreen)
    const canUseFunctions = ref(true)

    // Authentication status
    const isAuthenticated = computed(() => !!authStore.token)
    
    // Check if we're on a public route
    const isPublicRoute = computed(() => {
      const publicRoutes = ['/', '/login', '/register', '/forgot-password', '/reset-password', 
                          '/auth-callback', '/about', '/contact', '/help', '/faq']
      return publicRoutes.includes(route.path)
    })
    
    // Check if we're on the user dashboard
    const isUserDashboard = computed(() => route.path === '/user/dashboard')

    // Chat title handling
    const chatTitle = computed(() => {
      try {
        if (chatStore.currentChat) {
          return chatStore.currentChat.title
        }
        return chatStore.contextTitle || 'AI Learning Assistant'
      } catch (e) {
        return 'AI Learning Assistant'
      }
    })

    // Watch for route changes to update button visibility
    watch(() => route.path, () => {
      updateButtonVisibility()
    })
    
    // Watch for changes in the chat store's open state
    watch(() => chatStore.isOpen, (newVal) => {
      isOpen.value = newVal
    })
    
    // Watch our local open state and sync to store
    watch(isOpen, (newVal) => {
      chatStore.isOpen = newVal
      
      // When opening, make sure we have a valid chat
      if (newVal) {
        ensureValidChat()
      }
    })

    // Open chat
    const openChat = () => {
      ensureValidChat()
      isOpen.value = true
      console.log("Chat opened, now open:", isOpen.value)
    }

    // Close chat
    const closeChat = () => {
      isOpen.value = false
      console.log("Chat closed, now open:", isOpen.value)
    }
    
    // Toggle split screen
    const toggleSplitScreen = () => {
      chatStore.toggleSplitScreen()
    }

    // Helper function to ensure we have a valid chat
    const ensureValidChat = () => {
      try {
        if (chatStore.chatHistory.length === 0) {
          startNewChat()
          return
        }
        
        if (!chatStore.currentChatId && chatStore.chatHistory.length > 0) {
          selectChat(chatStore.chatHistory[0].id)
        }
      } catch (e) {
        console.error("Error ensuring valid chat:", e)
        startNewChat()
      }
    }

    // Start a new chat
    const startNewChat = () => {
      try {
        chatStore.startNewChat('New Conversation')
        showHistory.value = false
      } catch (e) {
        console.error("Error starting new chat:", e)
      }
    }

    // Select a chat
    const selectChat = (chatId) => {
      try {
        // Ensure chatId is treated correctly whether string or number
        const targetChatId = chatId ? chatId.toString() : null
        const targetChat = chatStore.chatHistory.find(c => c.id.toString() === targetChatId)
        
        if (!targetChat) {
          console.error(`Chat with ID ${chatId} not found`)
          return
        }
        
        chatStore.setCurrentChat(targetChat.id)
        showHistory.value = false
      } catch (e) {
        console.error("Error selecting chat:", e)
      }
    }

    // Delete a chat
    const deleteChat = (chatId) => {
      try {
        chatStore.deleteChat(chatId)
      } catch (e) {
        console.error("Error deleting chat:", e)
      }
    }

    // Toggle history sidebar
    const toggleHistory = () => {
      showHistory.value = !showHistory.value
    }

    // Update button visibility based on current route
    const updateButtonVisibility = () => {
      if (isUserDashboard.value) {
        shouldShowButton.value = false
      } else {
        shouldShowButton.value = true
      }
    }

    // Format date for display
    const formatDate = (date) => {
      try {
        if (!date) return "Just now"
        
        const now = new Date()
        const diff = now - new Date(date)
        
        // Less than a day
        if (diff < 86400000) {
          const hours = Math.floor(diff / 3600000)
          if (hours < 1) {
            return 'Just now'
          } else if (hours === 1) {
            return '1 hour ago'
          } else {
            return `${hours} hours ago`
          }
        }
        
        // Less than a week
        if (diff < 604800000) {
          const days = Math.floor(diff / 86400000)
          if (days === 1) {
            return 'Yesterday'
          } else {
            return `${days} days ago`
          }
        }
        
        // Format as date
        return new Date(date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
      } catch (e) {
        return "Unknown date"
      }
    }

    // Initialize component
    onMounted(async () => {
      try {
        console.log("GlobalChat mounted, route:", route.path)
        
        // Update button visibility based on route
        updateButtonVisibility()
        
        // Sync with store
        isOpen.value = chatStore.isOpen
        
        // Make sure chat store is initialized
        if (!chatStore.initialized) {
          chatStore.initialize()
        }
        
        // Check if AI can use functions
        canUseFunctions.value = await ChatService.canUseFunctions()
      } catch (e) {
        console.error("Error in GlobalChat onMounted:", e)
      }
    })

    return {
      // References to stores
      chatStore,
      
      // Local state
      isOpen,
      showHistory,
      shouldShowButton,
      isSplitScreen,
      canUseFunctions,
      
      // Computed properties
      isAuthenticated,
      isPublicRoute,
      isUserDashboard,
      chatTitle,
      
      // Methods
      openChat,
      closeChat,
      toggleSplitScreen,
      toggleHistory,
      selectChat,
      deleteChat,
      startNewChat,
      formatDate,
      ensureValidChat
    }
  }
}
</script>

<style scoped>
.chat-container {
  position: relative;
  z-index: 100;
}

/* Chat Panel */
.chat-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 400px;
  background-color: #fff;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 99999;
  overflow: hidden;
  border-left: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.chat-panel.full-screen {
  width: 100%;
  border-left: none;
}

/* Chat Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.context-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #fee2e2;
  color: #991b1b;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.function-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.function-icon {
  font-size: 0.875rem;
  margin-right: 0.25rem;
}

.chat-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
}

/* History sidebar */
.history-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 300px;
  background-color: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  z-index: 100000;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.05);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.history-title {
  font-weight: 600;
  color: #111827;
  font-size: 1rem;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.chat-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.chat-list-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-list-item:hover {
  background-color: #f9fafb;
}

.chat-list-item.selected {
  background-color: #f3f4f6;
  border-left: 3px solid #991b1b;
}

.chat-item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-date {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Buttons */
.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  color: #6b7280;
  transition: all 0.2s;
  background: transparent;
}

.icon-button:hover {
  background-color: #e5e7eb;
  color: #111827;
}

.icon-button.active {
  background-color: #e5e7eb;
  color: #991b1b;
}

.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  color: #9ca3af;
  opacity: 0;
  transition: all 0.2s;
}

.chat-list-item:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background-color: #fee2e2;
  color: #991b1b;
}

.new-chat-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 8px;
  background-color: #991b1b;
  color: white;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.new-chat-button:hover {
  background-color: #7f1d1d;
}

/* Chat toggle button */
.chat-toggle-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background-color: #991b1b;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
  z-index: 99999;
}

.chat-toggle-button:hover {
  transform: scale(1.05);
  background-color: #7f1d1d;
}

.chat-tooltip {
  position: absolute;
  right: calc(100% + 12px);
  background-color: #1f2937;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(10px);
  pointer-events: none;
  transition: all 0.3s;
}

.chat-toggle-button:hover .chat-tooltip {
  opacity: 1;
  transform: translateX(0);
}

/* Transitions */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.3s ease;
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Scrollbar Styling */
.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-track {
  background: transparent;
}

.history-list::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 4px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}
</style> 