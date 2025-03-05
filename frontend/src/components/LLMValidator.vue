<!-- LLM Validator Component -->
<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-medium text-gray-900 mb-4">LLM Request Validator</h2>
    <p class="text-gray-600 mb-4">
      Validate if an LLM request might reveal sensitive information about graded assignments or academic integrity issues.
    </p>
    
    <div class="space-y-4">
      <div>
        <label for="llm-request" class="block text-sm font-medium text-gray-700">LLM Request Content</label>
        <textarea
          id="llm-request"
          v-model="requestContent"
          rows="4"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="Enter the LLM request content to validate..."
        ></textarea>
      </div>
      
      <div class="flex justify-end">
        <button
          @click="validateRequest"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          :disabled="isLoading"
        >
          <span v-if="isLoading">Validating...</span>
          <span v-else>Validate Request</span>
        </button>
      </div>
      
      <!-- Validation Results -->
      <div v-if="validationResult" class="mt-4">
        <div
          :class="[
            'p-4 rounded-md',
            validationResult.isValid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          ]"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <span
                v-if="validationResult.isValid"
                class="material-symbols-outlined text-green-600"
              >
                check_circle
              </span>
              <span
                v-else
                class="material-symbols-outlined text-red-600"
              >
                error
              </span>
            </div>
            <div class="ml-3">
              <h3
                :class="[
                  'text-sm font-medium',
                  validationResult.isValid ? 'text-green-800' : 'text-red-800'
                ]"
              >
                {{ validationResult.isValid ? 'Request is valid' : 'Request contains sensitive content' }}
              </h3>
              <div
                :class="[
                  'mt-2 text-sm',
                  validationResult.isValid ? 'text-green-700' : 'text-red-700'
                ]"
              >
                <p>{{ validationResult.reason }}</p>
                
                <div v-if="validationResult.sensitiveContentDetails" class="mt-2">
                  <p class="font-medium">Recommendation:</p>
                  <p>{{ validationResult.sensitiveContentDetails.recommendation }}</p>
                  
                  <div v-if="validationResult.sensitiveContentDetails.matchedPatterns.length > 0" class="mt-2">
                    <p class="font-medium">Matched patterns:</p>
                    <ul class="list-disc pl-5 mt-1">
                      <li v-for="(pattern, index) in validationResult.sensitiveContentDetails.matchedPatterns" :key="index">
                        {{ pattern }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { AcademicIntegrityService } from '@/services/academicIntegrity.service'

export default {
  name: 'LLMValidator',
  setup() {
    const requestContent = ref('')
    const validationResult = ref(null)
    const isLoading = ref(false)
    
    const validateRequest = async () => {
      if (!requestContent.value.trim()) {
        return
      }
      
      try {
        isLoading.value = true
        const result = await AcademicIntegrityService.validateLLMRequest(requestContent.value)
        validationResult.value = result
      } catch (error) {
        console.error('Error validating LLM request:', error)
        validationResult.value = {
          isValid: false,
          reason: 'An error occurred during validation',
          containsSensitiveContent: true,
          sensitiveContentDetails: {
            recommendation: 'Please try again later or contact support if the issue persists.'
          }
        }
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      requestContent,
      validationResult,
      isLoading,
      validateRequest
    }
  }
}
</script> 