<!-- LLM Chat Example Component with Academic Integrity Validation -->
<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-medium text-gray-900 mb-4">LLM Chat with Academic Integrity Protection</h2>
    
    <!-- Chat Messages -->
    <div class="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto mb-4">
      <div v-if="messages.length === 0" class="text-gray-500 text-center py-10">
        Start a conversation with the AI assistant
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="[
            'p-3 rounded-lg max-w-3/4',
            message.role === 'user' 
              ? 'bg-indigo-100 ml-auto' 
              : message.role === 'error'
                ? 'bg-red-100'
                : 'bg-gray-200'
          ]"
        >
          <p class="text-sm" v-if="message.role !== 'error'">{{ message.content }}</p>
          <div v-else>
            <p class="text-sm text-red-700 font-medium">{{ message.content }}</p>
            <p v-if="message.details?.recommendation" class="text-xs text-red-600 mt-1">
              {{ message.details.recommendation }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Area -->
    <div class="space-y-4">
      <div>
        <textarea
          v-model="userInput"
          rows="3"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="Type your message here..."
          @keydown.enter.prevent="sendMessage"
        ></textarea>
        <p v-if="showWarning" class="text-yellow-600 text-xs mt-1">
          <span class="material-symbols-outlined text-xs align-middle">warning</span>
          This message might contain academic integrity concerns. Please review before sending.
        </p>
      </div>
      
      <div class="flex justify-end">
        <button
          @click="sendMessage"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          :disabled="isLoading || !userInput.trim()"
        >
          <span v-if="isLoading">Sending...</span>
          <span v-else>Send</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { validateLLMRequest, mightContainAcademicIntegrityConcerns } from '@/utils/llmValidator'

export default {
  name: 'LLMChatExample',
  setup() {
    const userInput = ref('')
    const messages = ref([])
    const isLoading = ref(false)
    const showWarning = ref(false)
    
    // Watch user input for potential academic integrity concerns
    watch(userInput, (newValue) => {
      showWarning.value = mightContainAcademicIntegrityConcerns(newValue)
    })
    
    const sendMessage = async () => {
      if (!userInput.value.trim()) return
      
      // Add user message to chat
      messages.value.push({
        role: 'user',
        content: userInput.value
      })
      
      const userMessage = userInput.value
      userInput.value = ''
      isLoading.value = true
      
      try {
        // Validate the message for academic integrity concerns
        const validationResult = await validateLLMRequest(userMessage)
        
        if (!validationResult.isValid) {
          // Add error message to chat
          messages.value.push({
            role: 'error',
            content: validationResult.reason,
            details: validationResult.sensitiveContentDetails
          })
        } else {
          // Message is valid, simulate AI response
          setTimeout(() => {
            messages.value.push({
              role: 'assistant',
              content: 'This is a simulated response from the AI assistant. In a real implementation, this would be the response from your LLM service.'
            })
            isLoading.value = false
          }, 1000)
        }
      } catch (error) {
        console.error('Error sending message:', error)
        messages.value.push({
          role: 'error',
          content: 'An error occurred while processing your message. Please try again.'
        })
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      userInput,
      messages,
      isLoading,
      showWarning,
      sendMessage
    }
  }
}
</script> 