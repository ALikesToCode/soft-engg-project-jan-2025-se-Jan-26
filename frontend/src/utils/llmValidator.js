import { AcademicIntegrityService } from '@/services/academicIntegrity.service'

/**
 * Validates an LLM request for academic integrity concerns
 * 
 * @param {string} content - The content of the LLM request to validate
 * @returns {Promise<{isValid: boolean, reason: string, containsSensitiveContent: boolean, sensitiveContentDetails: object|null}>}
 */
export const validateLLMRequest = async (content) => {
  try {
    return await AcademicIntegrityService.validateLLMRequest(content)
  } catch (error) {
    console.error('Error validating LLM request:', error)
    // Return a safe default that blocks the request if validation fails
    return {
      isValid: false,
      reason: 'Validation service error. Request blocked for safety.',
      containsSensitiveContent: true,
      sensitiveContentDetails: null
    }
  }
}

/**
 * Higher-order function that wraps an LLM service function with validation
 * 
 * @param {Function} llmServiceFn - The LLM service function to wrap
 * @returns {Function} - A wrapped function that validates requests before passing them to the LLM service
 */
export const withLLMValidation = (llmServiceFn) => {
  return async (...args) => {
    // Assume the first argument is the content to validate
    const content = args[0]
    
    // Validate the content
    const validationResult = await validateLLMRequest(content)
    
    if (!validationResult.isValid) {
      // Return a standardized error response
      return {
        error: true,
        message: validationResult.reason,
        details: validationResult.sensitiveContentDetails,
        data: null
      }
    }
    
    // If valid, pass through to the original function
    return llmServiceFn(...args)
  }
}

/**
 * Simple function to check if a string contains academic integrity concerns
 * This is a synchronous version for quick client-side checks
 * 
 * @param {string} content - The content to check
 * @returns {boolean} - True if the content might contain academic integrity concerns
 */
export const mightContainAcademicIntegrityConcerns = (content) => {
  if (!content) return false
  
  const lowerContent = content.toLowerCase()
  const sensitivePatterns = [
    /(answer|solution)\s+(key|sheet)/,
    /(exam|test|quiz)\s+(answer|solution)/,
    /(grade|grading)\s+(curve|scale|rubric)/,
    /(cheat|plagiari[sz]e|plagiarism)/,
    /academic\s+(integrity|dishonesty)/,
    /(assignment|homework)\s+(answer|solution)/,
    /(exam|test)\s+question/,
    /(grade|score|mark)\s+(distribution|average)/,
    /(student|peer)\s+(grade|performance|score)/,
    /(answer|solve)\s+(for|my)\s+(assignment|homework|exam|quiz)/
  ]
  
  return sensitivePatterns.some(pattern => pattern.test(lowerContent))
} 