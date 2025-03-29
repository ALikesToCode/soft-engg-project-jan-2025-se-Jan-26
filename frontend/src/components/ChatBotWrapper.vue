<template>
  <div v-if="shouldShowPageChat" class="h-full flex flex-col">
    <!-- Floating Action Button (visible when in minimized mode) -->
    <button
      v-if="!isExpanded && !isSplitScreen"
      @click="toggleExpanded"
      class="fixed bottom-6 right-6 bg-maroon-600 text-white rounded-full p-4 shadow-lg hover:bg-maroon-700 transition-all z-50 group"
    >
      <span class="material-icons text-2xl">chat</span>
      <span class="absolute right-full mr-3 top-1/2 -translate-y-1/2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        Ask AI Assistant
      </span>
    </button>

    <!-- Floating Dialog (when expanded but not split screen) -->
    <div
      v-if="isExpanded && !isSplitScreen"
      class="fixed bottom-6 right-6 w-[800px] bg-white rounded-xl shadow-xl border border-gray-200 z-50 transition-all transform"
      :class="{'scale-95 opacity-0': !isExpanded, 'scale-100 opacity-100': isExpanded}"
    >
      <div class="flex items-center justify-between p-4 border-b border-gray-100">
        <div class="flex items-center space-x-3">
          <button
            @click="toggleHistory"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            :class="{ 'bg-gray-100': showHistory }"
            title="Toggle Chat History"
          >
            <span class="material-icons">history</span>
          </button>
          <h3 class="font-semibold text-gray-800">{{ currentChat ? currentChat.title : 'AI Learning Assistant' }}</h3>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="toggleSplitScreen"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            title="Toggle Split Screen"
          >
            <span class="material-icons">view_sidebar</span>
          </button>
          <button
            @click="toggleExpanded"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          >
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>
      <div class="flex h-[500px]">
        <!-- Chat History Sidebar -->
        <div v-if="showHistory" class="w-64 border-r border-gray-100 flex flex-col">
          <div class="p-3 border-b border-gray-100">
            <button
              @click="startNewChat"
              class="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
            >
              <span class="material-icons text-sm">add</span>
              <span>New Chat</span>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-1">
            <button
              v-for="chat in chatHistory"
              :key="chat.id"
              @click="selectChat(chat)"
              class="w-full text-left p-2 rounded-lg hover:bg-gray-100 transition-colors group"
              :class="{ 'bg-gray-100': currentChat?.id === chat.id }"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2 min-w-0">
                  <span class="material-icons text-gray-400 text-sm">chat</span>
                  <span class="text-sm text-gray-800 truncate">{{ chat.title }}</span>
                </div>
                <button 
                  @click.stop="deleteChat(chat)"
                  class="text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <span class="material-icons text-sm">delete</span>
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1 truncate">{{ formatDate(chat.lastUpdated) }}</p>
            </button>
          </div>
        </div>
        <!-- Chat Content -->
        <div class="flex-1 flex flex-col min-w-0">
          <ChatBotBox 
            :chat-id="currentChat?.id"
            :context="chatStore.currentContext"
            @update:title="updateChatTitle"
            @clear-context="clearContext"
          />
        </div>
      </div>
    </div>

    <!-- Split Screen Mode -->
    <div
      v-if="isSplitScreen"
      class="h-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-100"
    >
      <div class="flex items-center justify-between p-4 border-b border-gray-100">
        <div class="flex items-center space-x-3">
          <button
            @click="toggleHistory"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            :class="{ 'bg-gray-100': showHistory }"
            title="Toggle Chat History"
          >
            <span class="material-icons">history</span>
          </button>
          <h3 class="font-semibold text-gray-800">{{ currentChat ? currentChat.title : 'AI Learning Assistant' }}</h3>
        </div>
        <button
          @click="toggleSplitScreen"
          class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          title="Exit Split Screen"
        >
          <span class="material-icons">close_fullscreen</span>
        </button>
      </div>
      <div class="flex-1 min-h-0 flex">
        <!-- Chat History Sidebar -->
        <div v-if="showHistory" class="w-64 border-r border-gray-100 flex flex-col">
          <div class="p-3 border-b border-gray-100">
            <button
              @click="startNewChat"
              class="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
            >
              <span class="material-icons text-sm">add</span>
              <span>New Chat</span>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-1">
            <button
              v-for="chat in chatHistory"
              :key="chat.id"
              @click="selectChat(chat)"
              class="w-full text-left p-2 rounded-lg hover:bg-gray-100 transition-colors group"
              :class="{ 'bg-gray-100': currentChat?.id === chat.id }"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2 min-w-0">
                  <span class="material-icons text-gray-400 text-sm">chat</span>
                  <span class="text-sm text-gray-800 truncate">{{ chat.title }}</span>
                </div>
                <button 
                  @click.stop="deleteChat(chat)"
                  class="text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <span class="material-icons text-sm">delete</span>
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1 truncate">{{ formatDate(chat.lastUpdated) }}</p>
            </button>
          </div>
        </div>
        <!-- Chat Content -->
        <div class="flex-1 min-w-0">
          <ChatBotBox 
            :chat-id="currentChat?.id"
            :context="chatStore.currentContext"
            @update:title="updateChatTitle"
            @clear-context="clearContext"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChatBotBox from './ChatBotBox.vue'
import { useChatStore } from '@/stores/useChatStore'
import { ref, computed, onMounted, watch } from 'vue'

export default {
  name: 'ChatBotWrapper',
  components: {
    ChatBotBox
  },
  props: {
    pageChat: {
      type: Boolean,
      default: false
    },
    context: {
      type: Object,
      default: null
    }
  },
  emits: ['minimize'],
  setup(props, { emit }) {
    const chatStore = useChatStore()
    const loading = ref(false)
    
    // Check if page-specific chat should be shown
    const shouldShowPageChat = computed(() => {
      // Use a simple true value to always show chat
      // This avoids complicated logic that might cause issues
      return true
    })
    
    const isExpanded = ref(false)
    const isSplitScreen = ref(false)
    const showHistory = ref(false)
    
    // Handle missing currentChat safely
    const currentChat = computed(() => {
      return chatStore.currentChat || null
    })
    
    // Make sure we have a safe chatHistory to avoid errors
    const chatHistory = computed(() => {
      return chatStore.chatHistory || []
    })

    const toggleExpanded = () => {
      // Before expanding, make sure we have a valid chat
      ensureChatExists()
      isExpanded.value = !isExpanded.value
      if (!isExpanded.value) {
        isSplitScreen.value = false
        showHistory.value = false
      }
    }

    const toggleSplitScreen = () => {
      isSplitScreen.value = !isSplitScreen.value
      isExpanded.value = !isSplitScreen.value
    }

    const toggleHistory = () => {
      showHistory.value = !showHistory.value
    }

    // Helper function to ensure we have at least one chat
    const ensureChatExists = async () => {
      try {
        loading.value = true
        
        // Create a default chat if none exists
        if (chatStore.chatHistory.length === 0) {
          await startNewChat()
        }
        
        // Make sure we have a selected chat
        if (!chatStore.currentChatId && chatStore.chatHistory.length > 0) {
          await selectChat(chatStore.chatHistory[0].id)
        }
        
        return true
      } catch (e) {
        console.error("Error ensuring chat exists:", e)
        
        // Create a local fallback if needed
        if (chatStore.chatHistory.length === 0) {
          chatStore.chatHistory = [{
            id: "local-" + Date.now(),
            title: "New Chat",
            createdAt: new Date(),
            lastUpdated: new Date(),
            messages: []
          }]
          
          if (chatStore.chatHistory.length > 0) {
            chatStore.currentChatId = chatStore.chatHistory[0].id
          }
        }
        
        return false
      } finally {
        loading.value = false
      }
    }

    // Start a new chat with error handling
    const startNewChat = async () => {
      try {
        loading.value = true
        await chatStore.startNewChat('New Conversation')
        
        // Set context if provided
        if (props.context) {
          chatStore.setContext(props.context)
        }
        
        return true
      } catch (e) {
        console.error("Error starting new chat:", e)
        
        // Create a local fallback
        const newChatId = "local-" + Date.now()
        const newChat = {
          id: newChatId,
          title: "New Conversation",
          createdAt: new Date(),
          lastUpdated: new Date(),
          messages: []
        }
        
        chatStore.chatHistory.push(newChat)
        chatStore.currentChatId = newChatId
        
        // Set context if provided
        if (props.context) {
          chatStore.setContext(props.context)
        }
        
        return false
      } finally {
        loading.value = false
      }
    }

    // Select a chat with error handling
    const selectChat = async (chatId) => {
      try {
        loading.value = true
        await chatStore.setCurrentChat(chatId)
        return true
      } catch (e) {
        console.error("Error selecting chat:", e)
        
        // Try to set it directly
        chatStore.currentChatId = chatId
        return false
      } finally {
        loading.value = false
      }
    }

    // Delete a chat with error handling
    const deleteChat = async (chatId) => {
      try {
        loading.value = true
        await chatStore.deleteChat(chatId)
        return true
      } catch (e) {
        console.error("Error deleting chat:", e)
        
        // Try to delete it locally
        chatStore.chatHistory = chatStore.chatHistory.filter(chat => chat.id !== chatId)
        
        // If the deleted chat was selected, select another one
        if (chatStore.currentChatId === chatId) {
          if (chatStore.chatHistory.length > 0) {
            chatStore.currentChatId = chatStore.chatHistory[0].id
          } else {
            // Create a new one if all chats were deleted
            startNewChat()
          }
        }
        
        return false
      } finally {
        loading.value = false
      }
    }

    const updateChatTitle = (chatId, newTitle) => {
      try {
        chatStore.updateChatTitle(chatId, newTitle)
      } catch (error) {
        console.error('Error updating chat title:', error)
      }
    }

    // Clear context
    const clearContext = () => {
      chatStore.clearContext()
    }

    // Watch for changes in the current chat
    watch(() => chatStore.currentChat, (newChat) => {
      console.log('Current chat changed:', newChat)
    })

    // Initialize on mount
    onMounted(async () => {
      try {
        console.log("ChatBotWrapper mounted, pageChat:", props.pageChat)
        
        // Make sure chat store is initialized
        if (!chatStore.initialized) {
          console.log("Chat store not initialized, initializing now")
          await chatStore.initialize()
        }
        
        // Ensure chat exists
        await ensureChatExists()
        
        // Set context if provided
        if (props.context) {
          chatStore.setContext(props.context)
        }
      } catch (e) {
        console.error("Error in ChatBotWrapper onMounted:", e)
      }
    })

    return {
      chatStore,
      shouldShowPageChat,
      isExpanded,
      isSplitScreen,
      showHistory,
      currentChat,
      chatHistory,
      toggleExpanded,
      toggleSplitScreen,
      toggleHistory,
      startNewChat,
      selectChat,
      deleteChat,
      updateChatTitle,
      clearContext,
      formatDate,
      ensureChatExists
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for chat history */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.function-capabilities-badge {
  display: flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 9999px;
  color: #0369a1;
  font-size: 0.75rem;
}
</style> 