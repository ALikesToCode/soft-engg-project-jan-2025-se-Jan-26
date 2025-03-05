<template>
  <div class="flex flex-col h-full">
    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-500">
        <span class="material-icons text-4xl mb-2">chat</span>
        <p class="text-center">Start a new conversation with your AI Learning Assistant</p>
      </div>
      
      <div v-for="(message, index) in messages" 
           :key="index"
           class="flex items-start space-x-3"
           :class="{'justify-end': message.type === 'user'}"
      >
        <!-- AI Avatar -->
        <div v-if="message.type === 'ai'" class="flex-shrink-0">
          <div class="w-8 h-8 rounded-full bg-maroon-100 flex items-center justify-center">
            <span class="material-icons text-maroon-600 text-sm">smart_toy</span>
          </div>
        </div>
        
        <!-- Message Content -->
        <div
          class="rounded-lg px-4 py-2 max-w-[80%]"
          :class="{
            'bg-maroon-600 text-white': message.type === 'user',
            'bg-gray-100 text-gray-800': message.type === 'ai'
          }"
        >
          <div class="prose prose-sm" v-html="formatMessage(message.content)"></div>
          <div v-if="message.type === 'ai'" class="flex items-center space-x-2 mt-2 text-xs text-gray-500">
            <button class="hover:text-gray-700" @click="copyToClipboard(message.content)">
              <span class="material-icons text-sm">content_copy</span>
            </button>
            <button class="hover:text-gray-700" @click="thumbsUp(index)">
              <span class="material-icons text-sm">thumb_up</span>
            </button>
            <button class="hover:text-gray-700" @click="thumbsDown(index)">
              <span class="material-icons text-sm">thumb_down</span>
            </button>
          </div>
        </div>
        
        <!-- User Avatar -->
        <div v-if="message.type === 'user'" class="flex-shrink-0">
          <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <span class="material-icons text-gray-600 text-sm">person</span>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 rounded-full bg-maroon-100 flex items-center justify-center">
            <span class="material-icons text-maroon-600 text-sm">smart_toy</span>
          </div>
        </div>
        <div class="bg-gray-100 rounded-lg px-4 py-2">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-gray-100 p-4">
      <form @submit.prevent="sendMessage" class="flex items-end space-x-2">
        <div class="flex-1">
          <textarea
            v-model="newMessage"
            rows="1"
            placeholder="Type your message..."
            class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 resize-none"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown="handleKeyDown"
            ref="messageInput"
          ></textarea>
        </div>
        <button
          type="submit"
          class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!newMessage.trim() || isTyping"
        >
          <span class="material-icons">send</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import ChatService from '@/services/chat.service'

export default {
  name: 'ChatBotBox',
  props: {
    chatId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      isTyping: false,
      messageHistory: new Map() // Store messages for each chat
    }
  },
  watch: {
    chatId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          // Load messages for this chat
          this.messages = this.messageHistory.get(newId) || []
        } else {
          this.messages = []
        }
      }
    }
  },
  methods: {
    async sendMessage() {
      const message = this.newMessage.trim()
      if (!message || this.isTyping) return

      // Add user message
      this.messages.push({
        type: 'user',
        content: message
      })
      this.newMessage = ''
      this.scrollToBottom()

      // Save to history
      if (this.chatId) {
        this.messageHistory.set(this.chatId, [...this.messages])
      }

      // Simulate AI response
      this.isTyping = true
      await this.simulateTyping()
      
      // Add AI response
      const aiResponse = await this.getAIResponse(message)
      this.messages.push({
        type: 'ai',
        content: aiResponse
      })
      
      // Update chat title if it's the first message
      if (this.messages.length === 2) {
        this.$emit('update:title', this.chatId, this.generateChatTitle(message))
      }

      // Save to history again
      if (this.chatId) {
        this.messageHistory.set(this.chatId, [...this.messages])
      }

      this.isTyping = false
      this.scrollToBottom()
    },
    async simulateTyping() {
      // Simulate AI thinking time
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    },
    async getAIResponse(message) {
      try {
        const data = await ChatService.sendMessage(message);
        
        // Handle function calls if present
        if (data.function_calls && data.function_calls.length > 0) {
          let resultText = data.content + "\n\n";
          
          // Add information about function calls
          resultText += "I've gathered the following information:\n";
          
          for (const functionCall of data.function_calls) {
            resultText += `- Used ${functionCall.name} with parameters: ${JSON.stringify(functionCall.arguments)}\n`;
          }
          
          return resultText;
        }
        
        return data.content;
      } catch (error) {
        console.error("Error getting AI response:", error);
        return "I'm sorry, I encountered an error while processing your request. Please try again later.";
      }
    },
    generateChatTitle(message) {
      // Generate a title based on the first message
      return message.length > 30 ? message.substring(0, 30) + '...' : message
    },
    formatMessage(content) {
      // Convert markdown to HTML and sanitize
      const html = marked(content)
      return DOMPurify.sanitize(html)
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        container.scrollTop = container.scrollHeight
      })
    },
    handleKeyDown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        this.sendMessage()
      }
    },
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text)
        // TODO: Show success toast
      } catch (err) {
        // TODO: Show error toast
      }
    },
    thumbsUp(index) {
      // TODO: Implement feedback
      console.log('Thumbs up for message:', index)
    },
    thumbsDown(index) {
      // TODO: Implement feedback
      console.log('Thumbs down for message:', index)
    }
  }
}
</script>

<style scoped>
/* Hide scrollbar for Chrome, Safari and Opera */
.overflow-y-auto::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.overflow-y-auto {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

/* Markdown styles */
:deep(.prose) {
  max-width: none;
}

:deep(.prose pre) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.5rem;
  border-radius: 0.25rem;
  margin: 0.5rem 0;
}

:deep(.prose code) {
  color: inherit;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.1rem 0.25rem;
  border-radius: 0.25rem;
}
</style>
