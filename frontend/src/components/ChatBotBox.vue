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
import ChatService from '@/services/chat.service'
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
      swaggerError
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
  background-color: #f9fafb;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  max-width: 100%;
  animation: message-fade-in 0.3s ease;
}

.message-content {
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  position: relative;
  font-size: 0.9375rem;
  line-height: 1.5;
  overflow-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
  max-width: 85%;
}

.message.user {
  justify-content: flex-end;
}

.message.user .message-content {
  background-color: #991b1b;
  color: white !important;
  border-bottom-right-radius: 0.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message.user .message-content :deep(.prose) {
  color: white !important;
}

.message.user .message-content :deep(.prose *) {
  color: white !important;
}

.message.ai {
  justify-content: flex-start;
}

.message.ai .message-content {
  background-color: #f8fafc;
  color: #111827;
  border-bottom-left-radius: 0.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.message-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.message-action-btn {
  padding: 0.25rem;
  border-radius: 0.25rem;
  color: #6b7280;
  background-color: rgba(255, 255, 255, 0.9);
}

.message-action-btn:hover {
  color: #111827;
  background-color: rgba(255, 255, 255, 1);
}

.message.user .message-action-btn {
  background-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.message.user .message-action-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.feedback-buttons {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
}

.feedback-btn {
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  background-color: #f3f4f6;
  color: #4b5563;
  transition: all 0.2s;
}

.feedback-btn.active {
  background-color: #991b1b;
  color: white;
}

.feedback-btn:hover:not(.active) {
  background-color: #e5e7eb;
}

.chat-input-container {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: white;
}

.chat-input-wrapper {
  display: flex;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.chat-input {
  flex: 1;
  border: none;
  padding: 0.5rem;
  font-size: 0.875rem;
  resize: none;
  outline: none;
  min-height: 40px;
  max-height: 120px;
  background-color: transparent;
}

.send-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
  flex-shrink: 0;
  align-self: flex-end;
}

.send-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.send-button:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.send-button .material-icons {
  font-size: 1.25rem;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  width: fit-content;
  margin-bottom: 0.5rem;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #6b7280;
  margin: 0 2px;
  animation: typing-animation 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-animation {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

@keyframes message-fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.markdown-body pre {
  background-color: #1e293b;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.markdown-body code {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  color: #e5e7eb;
}

.markdown-body p {
  margin: 0.5rem 0;
}

.markdown-body ul, .markdown-body ol {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  padding: 2rem;
  color: #6b7280;
}

.empty-state-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #991b1b;
}

.empty-state-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-state-text {
  max-width: 24rem;
  line-height: 1.5;
}

.markdown-body {
  color: inherit;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  color: #111827;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.markdown-body strong {
  font-weight: 600;
  color: #111827;
}

.markdown-body a {
  color: #991b1b;
  text-decoration: underline;
}

.markdown-body a:hover {
  text-decoration: none;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
}

.markdown-body th,
.markdown-body td {
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
}

.markdown-body th {
  background-color: #f8fafc;
  font-weight: 600;
}

.function-calling-indicator {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
  width: fit-content;
  margin-bottom: 0.5rem;
  color: #0369a1;
}

.function-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
}

.function-text {
  font-size: 0.875rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.ai-typing-indicator, 
.function-executing {
  font-size: 0.75rem;
  padding: 0.5rem 0;
  text-align: center;
  color: #6b7280;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.25rem;
}

.typing-dot,
.executing-dot {
  width: 0.5rem;
  height: 0.5rem;
  background-color: #6b7280;
  border-radius: 50%;
  display: inline-block;
  margin: 0 0.125rem;
  animation: typing-animation 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(2),
.executing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3),
.executing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-animation {
  0%, 100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}

.swagger-tools {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.swagger-button {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 4px;
  transition: all 0.2s;
}

.swagger-button:hover {
  background-color: #e0f2fe;
}

.swagger-button .material-icons {
  font-size: 16px;
  margin-right: 4px;
}

.swagger-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.swagger-modal-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9fafb;
  border-radius: 8px 8px 0 0;
}

.swagger-modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.swagger-modal-content {
  position: relative;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.swagger-endpoints {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.swagger-help-text {
  margin-bottom: 16px;
  font-size: 0.875rem;
  color: #6b7280;
}

.swagger-endpoint-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.swagger-endpoint-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
}

.swagger-endpoint-item .method {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 6px;
  border-radius: 4px;
  margin-right: 8px;
  min-width: 50px;
  text-align: center;
  text-transform: uppercase;
  flex-shrink: 0;
}

.swagger-endpoint-item .method.get {
  background-color: #dbeafe;
  color: #1e40af;
}

.swagger-endpoint-item .method.post {
  background-color: #dcfce7;
  color: #15803d;
}

.swagger-endpoint-item .method.put {
  background-color: #fef9c3;
  color: #854d0e;
}

.swagger-endpoint-item .method.delete {
  background-color: #fee2e2;
  color: #b91c1c;
}

.swagger-endpoint-item .path {
  font-family: monospace;
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-right: 8px;
  flex-shrink: 0;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.swagger-endpoint-item .description {
  font-size: 0.875rem;
  color: #6b7280;
  flex: 1;
}

.swagger-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.swagger-loading .typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #0369a1;
  margin: 0 4px;
  animation: typing-animation 1.4s infinite ease-in-out both;
}

.swagger-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #b91c1c;
}

.swagger-error .material-icons {
  font-size: 32px;
  margin-bottom: 16px;
}

.swagger-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #6b7280;
}

.swagger-empty .material-icons {
  font-size: 32px;
  margin-bottom: 16px;
}

.modal-close-button {
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close-button:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.modal-close-button .material-icons {
  font-size: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
