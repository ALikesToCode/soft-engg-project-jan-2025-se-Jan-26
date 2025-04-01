<!-- LLM Chat Example Component with Academic Integrity Validation -->
<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-medium text-gray-900 mb-4">LLM Chat with Academic Integrity Protection</h2>
    
    <!-- Chat Messages -->
    <div class="bg-gray-50 rounded-lg p-4 h-[400px] overflow-y-auto mb-4" ref="chatContainer">
      <div v-if="messages.length === 0" class="text-gray-500 text-center py-10">
        Start a conversation with the AI assistant
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="[
            'p-3 rounded-lg max-w-[85%]',
            message.role === 'user' ? 'bg-indigo-100 ml-auto' : 
            message.role === 'error' ? 'bg-red-100' : 
            message.role === 'warning' ? 'bg-amber-100' : 'bg-gray-200'
          ]"
        >
          <div v-if="message.role === 'warning'" class="space-y-2">
            <div class="flex items-start">
              <span class="material-symbols-outlined text-amber-600 mr-2 mt-0.5">warning</span>
              <div>
                <p class="text-sm font-medium text-amber-800">Academic Integrity Alert</p>
                <p class="text-sm text-amber-700">{{ message.content }}</p>
              </div>
            </div>

            <div v-if="message.analysis" class="mt-2">
              <p class="text-xs font-medium text-amber-800">Integrity Score: {{ message.analysis.integrity_score }}/100</p>
              
              <!-- Flagged sections -->
              <div v-if="message.analysis.flags && message.analysis.flags.length > 0" class="mt-2 space-y-3">
                <div v-for="(flag, flagIndex) in message.analysis.flags" :key="flagIndex" class="text-xs">
                  <div class="flex items-center">
                    <span 
                      :class="[
                        'inline-block w-2 h-2 rounded-full mr-1',
                        flag.severity === 'high' ? 'bg-red-500' : 
                        flag.severity === 'medium' ? 'bg-amber-500' : 'bg-yellow-400'
                      ]"
                    ></span>
                    <span class="font-medium">{{ flag.type }}</span>
                    <span 
                      :class="[
                        'ml-2 px-1.5 py-0.5 rounded text-xs',
                        flag.severity === 'high' ? 'bg-red-100 text-red-800' : 
                        flag.severity === 'medium' ? 'bg-amber-100 text-amber-800' : 'bg-yellow-100 text-yellow-800'
                      ]"
                    >{{ flag.severity }}</span>
                  </div>
                  
                  <div class="ml-3 mt-1">
                    <p>{{ flag.explanation }}</p>
                    <div class="mt-1 p-1.5 bg-white rounded border border-amber-200">
                      <p class="italic">{{ flag.text }}</p>
                    </div>
                    <p class="mt-1 text-amber-700">
                      <span class="font-medium">Recommendation:</span> {{ flag.recommendation }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end mt-2 space-x-2">
              <button 
                @click="revealOriginalResponse(message)" 
                class="px-2 py-1 text-xs bg-amber-600 text-white rounded hover:bg-amber-700"
              >
                Show Response Anyway
              </button>
            </div>
          </div>
          
          <div v-else-if="message.role === 'error'" class="space-y-1">
            <div class="flex items-start">
              <span class="material-symbols-outlined text-red-600 mr-2 mt-0.5">error</span>
              <div>
                <p class="text-sm font-medium text-red-800">Error</p>
                <p class="text-sm text-red-700">{{ message.content }}</p>
              </div>
            </div>
          </div>
          
          <div v-else>
            <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
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
          <span v-if="isLoading">
            <span class="material-symbols-outlined animate-spin inline-block align-middle mr-1">progress_activity</span>
            {{ processingStep }}
          </span>
          <span v-else>Send</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import axios from 'axios'
import { AcademicIntegrityService } from '@/services/academicIntegrity.service'

export default {
  name: 'LLMChatIntegrityCheck',
  setup() {
    const userInput = ref('')
    const messages = ref([])
    const isLoading = ref(false)
    const showWarning = ref(false)
    const processingStep = ref('Sending')
    const chatContainer = ref(null)
    
    // Basic patterns to detect potential academic integrity concerns in user input
    const sensitivePatterns = [
      /\b(answer|solution)\s+(key|sheet)\b/i,
      /\b(exam|test|quiz)\s+(answer|solution)\b/i,
      /\b(cheat|plagiari[sz]e|plagiarism)\b/i,
      /\bacademic\s+(integrity|dishonesty)\b/i,
      /\b(assignment|homework)\s+(answer|solution)\b/i,
      /\b(solve|answer)\s+(for|my)\s+(assignment|homework|exam|quiz)\b/i
    ]
    
    // Check if text might contain academic integrity concerns
    const checkPotentialConcerns = (text) => {
      return sensitivePatterns.some(pattern => pattern.test(text))
    }
    
    // Watch user input for potential academic integrity concerns
    watch(userInput, (newValue) => {
      showWarning.value = checkPotentialConcerns(newValue)
    })
    
    // Scroll to bottom of chat
    const scrollToBottom = async () => {
      await nextTick()
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }
    
    // Send a message to the AI assistant
    const sendMessage = async () => {
      if (!userInput.value.trim() || isLoading.value) return
      
      // Add user message to chat
      messages.value.push({
        role: 'user',
        content: userInput.value
      })
      
      const userMessage = userInput.value
      userInput.value = ''
      isLoading.value = true
      processingStep.value = 'Sending'
      
      await scrollToBottom()
      
      try {
        // Simulate AI response - in a real app, this would call your backend API
        processingStep.value = 'Getting response'
        
        // Simulated LLM response - replace with actual API call in production
        await new Promise(resolve => setTimeout(resolve, 1000))
        const aiResponse = await simulateAIResponse(userMessage)
        
        // Now check the response for academic integrity issues
        processingStep.value = 'Checking integrity'
        const integrityResult = await AcademicIntegrityService.checkLLMResponse({
          response: aiResponse,
          query: userMessage
        })
        
        // If the response is flagged, show a warning
        if (integrityResult.flagged) {
          messages.value.push({
            role: 'warning',
            content: integrityResult.analysis.summary,
            analysis: integrityResult,
            originalResponse: aiResponse
          })
        } else {
          // Response is clean, show it directly
          messages.value.push({
            role: 'assistant',
            content: aiResponse
          })
        }
      } catch (error) {
        console.error('Error sending message:', error)
        messages.value.push({
          role: 'error',
          content: 'An error occurred while processing your message. Please try again.'
        })
      } finally {
        isLoading.value = false
        await scrollToBottom()
      }
    }
    
    // Function to reveal original response despite warning
    const revealOriginalResponse = (message) => {
      // Find the index of this warning message
      const index = messages.value.findIndex(m => m === message)
      if (index !== -1) {
        // Replace the warning with the actual response
        messages.value.splice(index, 1, {
          role: 'assistant',
          content: message.originalResponse
        })
      }
    }
    
    // Simulate an AI response - replace with actual API call in production
    const simulateAIResponse = async (query) => {
      // Sample responses for demonstration purposes
      const responses = {
        solution: `Here's the complete solution to Problem 3:

Step 1: First find the derivative of f(x) = 3x² - 2x + 5
f'(x) = 6x - 2

Step 2: To find critical points, set f'(x) = 0
6x - 2 = 0
6x = 2
x = 1/3

Step 3: Calculate f(1/3) 
f(1/3) = 3(1/3)² - 2(1/3) + 5
f(1/3) = 3/9 - 2/3 + 5
f(1/3) = -1/3 + 5
f(1/3) = 14/3

The answer is x = 1/3 and the minimum value is 14/3.`,
        
        guidance: `To approach Problem 3, you need to:

1. Find the derivative of the function f(x) = 3x² - 2x + 5
2. Set the derivative equal to zero to find critical points
3. Evaluate the function at those critical points

Try working through these steps and see what you get. The derivative should be a linear expression, and you should find one critical point. Let me know if you get stuck on a specific step.`,
        
        code: `# Here's the complete solution for your assignment:

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
        
    # Split array into halves
    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]
    
    # Recursively sort both halves
    left = merge_sort(left)
    right = merge_sort(right)
    
    # Merge the sorted halves
    return merge(left, right)
    
def merge(left, right):
    result = []
    i = j = 0
    
    # Compare elements from both halves and take the smaller one
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test with your example input
arr = [38, 27, 43, 3, 9, 82, 10]
print(f"Original array: {arr}")
sorted_arr = merge_sort(arr)
print(f"Sorted array: {sorted_arr}")`,
        
        default: `I understand you're asking about "${query}". This is a topic that requires careful consideration. 

To address your question effectively, I'd recommend breaking it down into smaller parts and approaching it step by step. Consider what concepts and principles are relevant here, and try to apply them systematically.

The key is to understand the fundamental ideas first, then build up to the more complex aspects. Would you like me to guide you through a particular aspect of this question in more detail?`
      }
      
      // Choose response based on query content
      if (/solution|answer|solve for me/i.test(query)) {
        return responses.solution
      } else if (/help|guide|approach|concept/i.test(query)) {
        return responses.guidance
      } else if (/code|program|function|algorithm/i.test(query)) {
        return responses.code
      } else {
        return responses.default
      }
    }
    
    return {
      userInput,
      messages,
      isLoading,
      showWarning,
      processingStep,
      chatContainer,
      sendMessage,
      revealOriginalResponse
    }
  }
}
</script> 