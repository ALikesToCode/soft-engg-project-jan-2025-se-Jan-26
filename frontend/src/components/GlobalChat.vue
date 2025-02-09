<template>
  <div v-if="shouldShowChat">
    <!-- Chat Panel -->
    <div 
      v-if="chatStore.isOpen"
      class="fixed inset-y-0 right-0 w-96 bg-white shadow-xl flex flex-col z-50 transform transition-transform duration-300"
      :class="[
        chatStore.isSplitScreen ? 'translate-x-0' : 'lg:relative lg:shadow-none lg:border-l lg:border-gray-200',
        !chatStore.isOpen && 'translate-x-full'
      ]"
    >
      <!-- Chat Header -->
      <div class="p-4 border-b border-gray-200 flex items-center justify-between bg-white">
        <div class="flex items-center space-x-3">
          <h2 class="text-lg font-semibold text-gray-900">{{ chatStore.contextTitle }}</h2>
          <span 
            v-if="chatStore.currentContext"
            class="px-2 py-0.5 bg-maroon-100 text-maroon-800 text-xs font-medium rounded-full"
          >
            {{ chatStore.currentContext.type }}
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <button 
            @click="chatStore.toggleSplitScreen"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            title="Toggle Split Screen"
          >
            <span class="material-icons">{{ chatStore.isSplitScreen ? 'close_fullscreen' : 'open_in_full' }}</span>
          </button>
          <button 
            @click="chatStore.closeChat"
            class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          >
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>

      <!-- Chat Content -->
      <ChatBotBox 
        class="flex-1" 
        :context="chatStore.currentContext"
        @clear-context="chatStore.clearContext"
      />
    </div>

    <!-- Toggle Chat Button -->
    <button
      v-if="!chatStore.isOpen"
      @click="chatStore.toggleChat"
      class="fixed bottom-6 right-6 bg-maroon-600 text-white rounded-full p-4 shadow-lg hover:bg-maroon-700 transition-all z-50 group"
    >
      <span class="material-icons">chat</span>
      <span class="absolute right-full mr-3 top-1/2 -translate-y-1/2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        Ask Learning Assistant
      </span>
    </button>
  </div>
</template>

<script>
import { useChatStore } from '@/stores/useChatStore'
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import ChatBotBox from './ChatBotBox.vue'

export default {
  name: 'GlobalChat',
  components: {
    ChatBotBox
  },
  setup() {
    const chatStore = useChatStore()
    const route = useRoute()

    const shouldShowChat = computed(() => {
      // Don't show on landing pages
      const landingPages = ['home', 'about', 'contact', 'login', 'register', 'faq']
      if (landingPages.includes(route.name)) return false

      // Only show if authenticated
      return chatStore.shouldShowChat
    })

    return {
      chatStore,
      shouldShowChat
    }
  }
}
</script>

<style scoped>
.translate-x-full {
  transform: translateX(100%);
}
</style> 