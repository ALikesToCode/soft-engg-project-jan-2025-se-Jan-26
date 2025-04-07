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
        <span class="material-icons animate-spin mr-2">settings</span>
        <span>Running functions...</span>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input-container">
      <div class="chat-options">
        <button 
          class="option-button"
          title="Clear Conversation"
          @click="clearConversation"
        >
          <span class="material-icons">delete_sweep</span>
        </button>
        <button 
          class="option-button"
          title="Toggle Precise Mode"
          @click="togglePreciseMode"
          :class="{'option-active': preciseModeActive}"
        >
          <span class="material-icons">travel_explore</span>
        </button>
      </div>
      <div class="chat-input">
        <textarea
          ref="messageInput"
          v-model="newMessage"
          placeholder="Ask me a question..."
          @keydown.enter.prevent="sendMessage"
          @input="resizeTextarea"
          class="chat-textarea"
          :disabled="isTyping || isFunctionCalling"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim() || isTyping || isFunctionCalling"
          class="send-button"
        >
          <span class="material-icons">send</span>
        </button>
      </div>
      
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
import ApiExecutorService from '@/services/api-executor.service'
import { useChatStore } from '@/stores/useChatStore'
import { computed, ref, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

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
    const preciseModeActive = ref(false)
    
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
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
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
        
        // Configure marked without syntax highlighting
        marked.setOptions({
          breaks: true,
          gfm: true,
          // Remove highlight function that uses highlight.js
          // highlight: (code, lang) => {
          //   if (hljs.getLanguage(lang)) {
          //     return hljs.highlight(code, { language: lang }).value
          //   }
          //   return hljs.highlightAuto(code).value
          // },
        })
        
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
        console.log("Getting AI response for message:", message)
        
        // Include context if available
        const payload = {
          id: threadId.value,
          query: message
        }
        
        console.log("ThreadID used:", threadId.value)
        
        if (props.context) {
          payload.context = props.context
          console.log("Context included:", props.context)
        }
        
        // Add model options based on precise mode
        payload.options = {
          use_grounding: true,
          use_fallback: false,
          temperature: preciseModeActive.value ? 0.1 : 0.7
        }
        
        console.log("Sending to ChatService with payload:", JSON.stringify(payload))
        const data = await ChatService.sendMessage(payload)
        
        // Check if we have a proper response
        if (!data) {
          console.error("Empty response from ChatService")
          return "I'm sorry, I couldn't generate a response. Please try again."
        }
        
        console.log("AI response received:", data)
        
        // Handle function calls if present
        if (data.function_calls && data.function_calls.length > 0) {
          // Show function calling indicator
          isFunctionCalling.value = true
          
          try {
            // Format the response to include function calls and results
            let response = data.content?.trim() || ""
            
            // Add function calls section
            response += "\n\n**Function Calls:**\n```js\n"
            data.function_calls.forEach(call => {
              response += `${call.name}(${JSON.stringify(call.arguments, null, 2)})\n`
            })
            response += "```\n"
            
            // Add function results section if available
            if (data.function_results && data.function_results.length > 0) {
              response += "\n**Results:**\n```json\n"
              data.function_results.forEach(result => {
                response += `${result.name} result: ${JSON.stringify(result.result, null, 2)}\n\n`
              })
              response += "```\n"
            }
            
            return response
          } catch (funcError) {
            console.error("Error processing function results:", funcError)
            return data.content + "\n\nI tried to process function results, but encountered an error: " + funcError.message
          } finally {
            // Hide function calling indicator
            isFunctionCalling.value = false
          }
        }
        
        // Regular response (no function calls)
        return data.content || "I apologize, but I couldn't generate a proper response."
      } catch (error) {
        console.error("Error getting AI response:", error)
        isFunctionCalling.value = false
        
        // Return a more user-friendly error message based on the error type
        if (error.response) {
          const status = error.response.status
          
          if (status === 401 || status === 403) {
            return "You need to be logged in to use this feature. Please sign in and try again."
          } else if (status === 404) {
            return "The AI service is currently unavailable. Please try again later."
          } else if (status >= 500) {
            return "The server encountered an issue. Our team has been notified and is working to fix it."
          }
        }
        
        return "I'm having trouble connecting to the AI service. Please check your internet connection and try again."
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
      const message = currentMessages.value[index]
      if (message) {
        console.log("Positive feedback for message:", message.id)
        // TODO: Send feedback to backend
      }
    }
    
    // Handle thumbs down feedback
    const thumbsDown = (index) => {
      const message = currentMessages.value[index]
      if (message) {
        console.log("Negative feedback for message:", message.id)
        // TODO: Send feedback to backend
      }
    }
    
    // Clear chat history
    const clearChat = async () => {
      try {
        // First attempt to clear via the service (which will try API first, then local)
        const result = await ChatService.clearChatHistory(props.chatId)
        
        // Update the store (this should work even if the API call failed)
        await chatStore.clearChatHistory(props.chatId)
        
        // Check if there was an error in the API response
        if (result && result.error) {
          console.warn("API error when clearing chat, but local cache was cleared:", result.error)
        }
      } catch (err) {
        console.error("Failed to clear chat:", err)
        
        // Fallback: Try to at least clear the local store
        try {
          await chatStore.clearChatHistory(props.chatId)
          console.log("Cleared chat locally despite API error")
        } catch (storeErr) {
          console.error("Failed to clear chat even locally:", storeErr)
        }
      }
    }
    
    // Toggle Swagger documentation modal
    const toggleSwaggerInfo = async () => {
      try {
        // Toggle the visibility
        showSwaggerInfo.value = !showSwaggerInfo.value
        
        // If showing and we don't have endpoints loaded yet, fetch them
        if (showSwaggerInfo.value && swaggerEndpoints.value.length === 0) {
          loadingSwagger.value = true
          swaggerError.value = null
          
          try {
            // Use the ChatService to get the Swagger endpoints
            const endpoints = await ChatService.getSwaggerEndpoints()
            swaggerEndpoints.value = endpoints
          } catch (error) {
            console.error("Error loading API documentation:", error)
            swaggerError.value = "Failed to load API documentation"
          } finally {
            loadingSwagger.value = false
          }
        }
      } catch (err) {
        console.error("Error toggling Swagger info:", err)
        swaggerError.value = "An error occurred"
      }
    }
    
    // Clear the current conversation history
    const clearConversation = async () => {
      if (!props.chatId) return
      
      try {
        // Call the service to clear the conversation on the backend
        const result = await ChatService.clearConversation(props.chatId)
        
        if (result.success) {
          // Clear the local chat store
          chatStore.clearMessages(props.chatId)
          
          // Add a system message indicating the conversation was cleared
          await chatStore.addMessage(props.chatId, {
            id: Date.now() + '-system',
            role: 'system',
            type: 'ai',
            content: "Conversation has been cleared. How can I help you today?",
            timestamp: new Date()
          })
        } else {
          console.error("Failed to clear conversation:", result.message)
        }
      } catch (error) {
        console.error("Error clearing conversation:", error)
      }
    }
    
    // Toggle precise mode
    const togglePreciseMode = () => {
      preciseModeActive.value = !preciseModeActive.value
      console.log("Precise mode:", preciseModeActive.value ? "enabled" : "disabled")
      
      // Add a system message to indicate the mode change
      if (props.chatId) {
        chatStore.addMessage(props.chatId, {
          id: Date.now() + '-system',
          role: 'system',
          type: 'ai',
          content: preciseModeActive.value 
            ? "Precise mode enabled. I'll focus on accuracy and detailed information."
            : "Precise mode disabled. I'll provide more creative and conversational responses.",
          timestamp: new Date()
        })
      }
    }
    
    // Resize textarea as content grows
    const resizeTextarea = () => {
      const textarea = messageInput.value
      if (!textarea) return
      
      // Reset height to auto to get proper scrollHeight
      textarea.style.height = 'auto'
      
      // Set new height based on scrollHeight, with max height
      const newHeight = Math.min(textarea.scrollHeight, 150)
      textarea.style.height = `${newHeight}px`
      
      // Scroll to bottom after resize
      scrollToBottom()
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
      clearChat,
      toggleSwaggerInfo,
      clearConversation,
      togglePreciseMode,
      preciseModeActive,
      resizeTextarea
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

.chat-options {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
  gap: 8px;
}

.option-button {
  background: none;
  border: none;
  cursor: pointer;
  color: #6c757d;
  border-radius: 4px;
  padding: 4px;
  transition: all 0.2s;
}

.option-button:hover {
  background-color: #f1f3f5;
  color: #495057;
}

.option-active {
  background-color: #e6f7ff;
  color: #0084ff;
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background-color: #fff;
  border-radius: 24px;
  border: 1px solid #dee2e6;
  overflow: hidden;
  padding-left: 16px;
}

.chat-textarea {
  flex: 1;
  border: none;
  padding: 12px 0;
  resize: none;
  min-height: 24px;
  max-height: 150px;
  outline: none;
  font-size: 14px;
  line-height: 1.5;
  font-family: inherit;
  background: transparent;
}

.send-button {
  border: none;
  background: none;
  cursor: pointer;
  color: #0084ff;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.send-button:hover {
  color: #0056b3;
}

.send-button:disabled {
  color: #adb5bd;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 18px;
  background-color: #e9ecef;
  margin-bottom: 12px;
  align-self: flex-start;
  width: 60px;
}

.function-calling-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 18px;
  background-color: #fff3cd;
  color: #856404;
  margin-bottom: 12px;
  align-self: flex-start;
  font-size: 0.875rem;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background-color: #6c757d;
  border-radius: 50%;
  margin: 0 2px;
  animation: typingAnimation 1.4s infinite both;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingAnimation {
  0%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-2px);
  }
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

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Basic code styling without highlight.js */
.prose code {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  padding: 2px 4px;
  font-family: monospace;
  font-size: 0.875em;
}

.prose pre {
  background-color: #f1f3f5;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
  display: block;
  overflow-x: auto;
  color: #333;
  white-space: pre;
}
</style>
