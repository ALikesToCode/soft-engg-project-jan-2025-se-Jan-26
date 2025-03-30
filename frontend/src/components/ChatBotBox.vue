<template>
  <div class="chat-container">
    <!-- Messages Area -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="currentMessages.length === 0" class="empty-state">
        <span class="empty-state-icon material-icons text-4xl mb-2">chat</span>
        <p class="empty-state-title">Hello, how can I help you today?</p>
        <p class="empty-state-text">Ask me any question about your courses, assignments, or academic materials.</p>
      </div>
      
      <div v-for="(message, index) in currentMessages" 
           :key="index"
           class="message"
           :class="{'user': message.type === 'user', 'ai': message.type === 'ai'}"
      >
        <!-- Message Content -->
        <div class="message-content" :class="{'user': message.type === 'user', 'ai': message.type === 'ai'}">
          <div class="prose prose-sm" v-html="formatMessage(message.content)"></div>
          <div v-if="message.type === 'ai'" class="message-actions">
            <button class="message-action-btn hover:text-gray-700" @click="copyToClipboard(message.content)">
              <span class="material-icons text-sm">content_copy</span>
            </button>
            <button class="message-action-btn hover:text-gray-700" @click="thumbsUp(index)">
              <span class="material-icons text-sm">thumb_up</span>
            </button>
            <button class="message-action-btn hover:text-gray-700" @click="thumbsDown(index)">
              <span class="material-icons text-sm">thumb_down</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
      
      <!-- Function Calling Indicator -->
      <div v-if="isFunctionCalling" class="function-calling-indicator">
        <div class="function-icon">
          <span class="material-icons">functions</span>
        </div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="function-text">Executing functions</div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input-container">
      <div class="swagger-tools">
        <button class="swagger-button" @click="toggleSwaggerInfo">
          <span class="material-icons">api</span>
          API Docs
        </button>
        
        <button v-if="currentMessages.length > 0" class="swagger-button clear-button" @click="clearChat">
          <span class="material-icons">delete</span>
          Clear Chat
        </button>
      </div>
      
      <form @submit.prevent="sendMessage" class="chat-input-wrapper">
        <textarea
          v-model="newMessage"
          rows="1"
          placeholder="Type your message..."
          class="chat-input"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown="handleKeyDown"
          ref="messageInput"
        ></textarea>
        <button
          type="submit"
          class="send-button"
          :disabled="!newMessage.trim() || isTyping || isFunctionCalling"
        >
          <span class="material-icons">send</span>
        </button>
      </form>
      
      <!-- Swagger Modal -->
      <Transition name="fade">
        <div v-if="showSwaggerInfo" class="swagger-modal" @click.self="showSwaggerInfo = false">
          <div class="swagger-modal-content">
            <div class="swagger-modal-header">
              <h3>Available API Endpoints</h3>
              <button @click="showSwaggerInfo = false" class="modal-close-button">
                <span class="material-icons">close</span>
              </button>
            </div>
            
            <div class="swagger-endpoints">
              <div v-if="loadingSwagger" class="swagger-loading">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
              </div>
              
              <div v-else-if="swaggerError" class="swagger-error">
                <span class="material-icons">error</span>
                <p>{{ swaggerError }}</p>
              </div>
              
              <template v-else>
                <p class="swagger-help-text">
                  These endpoints are available to the AI assistant. You can ask it to retrieve or manipulate data through these APIs.
                </p>
                
                <ul v-if="swaggerEndpoints.length > 0" class="swagger-endpoint-list">
                  <li v-for="(endpoint, index) in swaggerEndpoints" :key="index" class="swagger-endpoint-item">
                    <div :class="['method', endpoint.method.toLowerCase()]">{{ endpoint.method }}</div>
                    <div class="path">{{ endpoint.path }}</div>
                    <div class="description">{{ endpoint.description || 'No description available' }}</div>
                  </li>
                </ul>
                
                <div v-else class="swagger-empty">
                  <span class="material-icons">info</span>
                  <p>No API endpoints found</p>
                </div>
              </template>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ChatService } from '@/services/chat.service'
import { useChatStore } from '@/stores/useChatStore'
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'ChatBotBox',
  props: {
    chatId: {
      type: String,
      default: null
    },
    context: {
      type: Object,
      default: null
    }
  },
  emits: ['clear-context', 'update:title'],
  setup(props, { emit }) {
    const route = useRoute()
    const chatStore = useChatStore()
    const newMessage = ref('')
    const isTyping = ref(false)
    const isFunctionCalling = ref(false)
    const messagesContainer = ref(null)
    const messageInput = ref(null)
    const swaggerEndpoints = ref([])
    const showSwaggerInfo = ref(false)
    const loadingSwagger = ref(false)
    const swaggerError = ref(null)
    
    // Get the current chat's messages from the chat store
    const currentMessages = computed(() => {
      const chatId = props.chatId
      if (!chatId) return []
      
      const chat = chatStore.chatHistory.find(chat => chat.id === chatId)
      return chat ? chat.messages : []
    })
    
    // Get or generate a thread ID for this chat
    const threadId = computed(() => {
      const chat = chatStore.chatHistory.find(chat => chat.id === props.chatId)
      return chat?.threadId || crypto.randomUUID()
    })
    
    // Watch for changes in chatId and scroll to bottom
    watch(() => props.chatId, () => {
      scrollToBottom()
    })
    
    onMounted(() => {
      scrollToBottom()
    })
    
    // Scroll to the bottom of the chat
    const scrollToBottom = () => {
      setTimeout(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      }, 100)
    }
    
    // Format message content with markdown - with type checking
    const formatMessage = (content) => {
      try {
        // Ensure content is a string
        if (typeof content !== 'string') {
          // If it's an object, try to stringify it
          if (content && typeof content === 'object') {
            content = JSON.stringify(content)
          } else {
            // If it's another type or null/undefined, provide a fallback
            content = String(content || 'Message unavailable')
          }
        }
        
        const html = marked(content)
        return DOMPurify.sanitize(html)
      } catch (error) {
        console.error('Error formatting message:', error)
        return 'Error displaying message'
      }
    }
    
    // Handle key events
    const handleKeyDown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        sendMessage()
      }
    }
    
    // Send a message
    const sendMessage = async () => {
      const message = newMessage.value.trim()
      if (!message || isTyping.value || isFunctionCalling.value) return
      
      // Create a chat if none exists
      if (!props.chatId) {
        const newChatId = chatStore.startNewChat('New Conversation')
        emit('update:chatId', newChatId)
      }
      
      // Clear input and scroll
      newMessage.value = ''
      
      try {
        // Add user message to the store ONLY
        const userMessage = {
          id: Date.now() + '-user',
          role: 'user',
          type: 'user',
          content: message,
          timestamp: new Date()
        }
        
        // Add user message to chat history
        await chatStore.addMessage(props.chatId, userMessage)
        
        // Update chat title if it's the first message
        if (currentMessages.value.length === 1) { // Just added the first message
          const title = generateChatTitle(message)
          chatStore.updateChatTitle(props.chatId, title)
        }
        
        scrollToBottom()
        
        // Get AI response
        isTyping.value = true
        await simulateTyping()
        
        const response = await getAIResponse(message)
        
        // Add AI response to chat history
        await chatStore.addMessage(props.chatId, {
          id: Date.now() + '-ai',
          role: 'assistant',
          type: 'ai',
          content: response,
          timestamp: new Date()
        })
        
      } catch (error) {
        console.error("Error getting AI response:", error)
        
        // Add error message
        await chatStore.addMessage(props.chatId, {
          id: Date.now() + '-ai',
          role: 'assistant',
          type: 'ai',
          content: "I'm sorry, I encountered an error while processing your request. Please try again later.",
          timestamp: new Date()
        })
      } finally {
        isTyping.value = false
        scrollToBottom()
      }
    }
    
    // Simulate AI typing
    const simulateTyping = async () => {
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1500))
    }
    
    // Get AI response from backend
    const getAIResponse = async (message) => {
      try {
        // Include context if available
        const payload = {
          id: threadId.value,
          query: message
        }
        
        if (props.context) {
          payload.context = props.context
        }
        
        const data = await ChatService.sendMessage(payload)
        
        // Check if we have a proper response
        if (!data) {
          return "I'm sorry, I couldn't generate a response. Please try again."
        }
        
        // Handle function calls if present (if backend returns them)
        if (data.function_calls && data.function_calls.length > 0) {
          // Show function calling indicator
          isFunctionCalling.value = true
          
          // First part of the response (before function calls)
          let response = data.content?.trim() || ""
          
          // Wait a moment to simulate the time for function execution 
          // (this would actually be happening on the backend)
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          // Format function calls in a more readable way
          const functionCallsFormatted = data.function_calls.map(fc => {
            const functionName = fc.name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
            const args = Object.entries(fc.arguments || {})
              .map(([key, value]) => `${key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
              .join('\n- ');
              
            return `**${functionName}**\n- ${args}`;
          }).join('\n\n');
          
          // Add function calls section
          response += '\n\n---\n\n';
          response += '### I used these functions to get information:\n\n';
          response += functionCallsFormatted;
          
          // Hide function calling indicator
          isFunctionCalling.value = false
          
          return response;
        }
        
        // Regular response (no function calls)
        return data.content || "I apologize, but I couldn't generate a proper response."
      } catch (error) {
        console.error("Error getting AI response:", error)
        isFunctionCalling.value = false
        throw error
      }
    }
    
    // Generate a title based on the first message
    const generateChatTitle = (message) => {
      return message.length > 30 ? message.substring(0, 30) + '...' : message
    }
    
    // Copy message to clipboard
    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        // TODO: Show success toast
      } catch (err) {
        console.error("Failed to copy:", err)
        // TODO: Show error toast
      }
    }
    
    // Handle thumbs up feedback
    const thumbsUp = (index) => {
      // TODO: Implement feedback
      console.log('Thumbs up for message:', index)
    }
    
    // Handle thumbs down feedback
    const thumbsDown = (index) => {
      // TODO: Implement feedback
      console.log('Thumbs down for message:', index)
    }
    
    // Clear chat history
    const clearChat = async () => {
      try {
        await ChatService.clearChatHistory(props.chatId)
        await chatStore.clearChatHistory(props.chatId)
        // TODO: Show success toast
      } catch (err) {
        console.error("Failed to clear chat:", err)
        // TODO: Show error toast
      }
    }
    
    return {
      currentMessages,
      newMessage,
      isTyping,
      isFunctionCalling,
      messagesContainer,
      messageInput,
      chatStore,
      sendMessage,
      formatMessage,
      scrollToBottom,
      handleKeyDown,
      copyToClipboard,
      thumbsUp,
      thumbsDown,
      swaggerEndpoints,
      showSwaggerInfo,
      loadingSwagger,
      swaggerError,
      clearChat
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

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  opacity: 0.7;
  padding: 2rem;
}

.empty-state-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-state-text {
  font-size: 0.875rem;
  max-width: 300px;
}

.message {
  display: flex;
  margin-bottom: 1rem;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message.ai {
  margin-right: auto;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  position: relative;
}

.message-content.user {
  background-color: #e7f2ff;
  color: #0d47a1;
  border-top-right-radius: 0;
}

.message-content.ai {
  background-color: #f0f0f0;
  color: #333;
  border-top-left-radius: 0;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  justify-content: flex-end;
}

.message-action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.chat-input-container {
  border-top: 1px solid #e0e0e0;
  padding: 1rem;
  background-color: white;
}

.chat-input-wrapper {
  display: flex;
  border: 1px solid #e0e0e0;
  border-radius: 1.5rem;
  padding: 0.5rem 0.75rem;
  background-color: white;
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  resize: none;
  background: transparent;
  max-height: 120px;
}

.send-button {
  background: none;
  border: none;
  color: #4299e1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:disabled {
  color: #a0aec0;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f0f0f0;
  border-radius: 1rem;
  max-width: 60px;
  margin-right: auto;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #888;
  margin: 0 2px;
  animation: typing 1.5s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.5s;
}

.typing-dot:nth-child(3) {
  animation-delay: 1s;
}

.function-calling-indicator {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f0f2ff;
  border: 1px solid #e0e6ff;
  border-radius: 1rem;
  max-width: 200px;
  margin-right: auto;
}

.function-icon {
  margin-right: 8px;
  color: #4f46e5;
}

.function-text {
  font-size: 0.75rem;
  color: #4f46e5;
  margin-left: 8px;
}

.swagger-tools {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
  gap: 8px;
}

.swagger-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f5f5f5;
  font-size: 12px;
  cursor: pointer;
}

.swagger-button:hover {
  background-color: #e9e9e9;
}

.clear-button {
  background-color: #fff1f1;
  border-color: #ffcfcf;
  color: #e53e3e;
}

.clear-button:hover {
  background-color: #ffeded;
}

.swagger-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.swagger-modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 70vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.swagger-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-close-button {
  background: none;
  border: none;
  cursor: pointer;
}

.swagger-endpoints {
  padding: 1rem;
  max-height: 60vh;
  overflow-y: auto;
}

.swagger-help-text {
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.swagger-endpoint-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.swagger-endpoint-item {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.swagger-endpoint-item:last-child {
  border-bottom: none;
}

.method {
  font-weight: bold;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.method.get {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.method.post {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.method.put {
  background-color: #fff3e0;
  color: #e65100;
}

.method.delete {
  background-color: #ffebee;
  color: #b71c1c;
}

.path {
  font-family: monospace;
}

.description {
  font-size: 0.875rem;
  color: #666;
  flex-basis: 100%;
}

.swagger-loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.swagger-error {
  color: #e53e3e;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
}

.swagger-empty {
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
}

@keyframes typing {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
