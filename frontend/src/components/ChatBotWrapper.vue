<template>
  <div>
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
            @update:title="updateChatTitle"
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
            @update:title="updateChatTitle"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChatBotBox from './ChatBotBox.vue'

export default {
  name: 'ChatBotWrapper',
  components: {
    ChatBotBox
  },
  data() {
    return {
      isExpanded: false,
      isSplitScreen: false,
      showHistory: false,
      currentChat: null,
      chatHistory: [
        {
          id: 1,
          title: 'Python Programming Help',
          lastUpdated: new Date('2024-01-25T10:30:00'),
          messages: []
        },
        {
          id: 2,
          title: 'Data Structures Concepts',
          lastUpdated: new Date('2024-01-24T15:45:00'),
          messages: []
        },
        {
          id: 3,
          title: 'Web Development Questions',
          lastUpdated: new Date('2024-01-23T09:15:00'),
          messages: []
        }
      ]
    }
  },
  methods: {
    toggleExpanded() {
      this.isExpanded = !this.isExpanded
      if (!this.isExpanded) {
        this.isSplitScreen = false
        this.showHistory = false
      }
    },
    toggleSplitScreen() {
      this.isSplitScreen = !this.isSplitScreen
      this.isExpanded = !this.isSplitScreen
    },
    toggleHistory() {
      this.showHistory = !this.showHistory
    },
    startNewChat() {
      const newChat = {
        id: Date.now(),
        title: 'New Conversation',
        lastUpdated: new Date(),
        messages: []
      }
      this.chatHistory.unshift(newChat)
      this.selectChat(newChat)
    },
    selectChat(chat) {
      this.currentChat = chat
    },
    deleteChat(chatToDelete) {
      this.chatHistory = this.chatHistory.filter(chat => chat.id !== chatToDelete.id)
      if (this.currentChat?.id === chatToDelete.id) {
        this.currentChat = this.chatHistory[0] || null
      }
    },
    updateChatTitle(chatId, newTitle) {
      const chat = this.chatHistory.find(c => c.id === chatId)
      if (chat) {
        chat.title = newTitle
        chat.lastUpdated = new Date()
      }
    },
    formatDate(date) {
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (days === 0) {
        return 'Today'
      } else if (days === 1) {
        return 'Yesterday'
      } else if (days < 7) {
        return `${days} days ago`
      } else {
        return date.toLocaleDateString()
      }
    }
  }
}
</script>

<style scoped>
.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s ease-in-out;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

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
</style> 